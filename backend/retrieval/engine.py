"""End-to-end retrieval pipeline with early security filtering."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
import hashlib, re, time
from .embeddings import EmbeddingProvider, MockEmbeddingProvider
from .models import *
from .ranking import deduplicate, rank
from .security import allowed_scopes, may_access
from .vectorstore import InMemoryVectorStore, VectorStore

def normalize_query(value: str) -> str:
    return " ".join(re.findall(r"\w+", value.casefold(), re.UNICODE))

class RetrievalCache:
    def __init__(self): self._items = {}
    def key(self, q: RetrievalQuery, version: int):
        material = (q.normalized_query, q.requester.casefold(), tuple(sorted(q.domains)), q.security_scope,
                    tuple(sorted(q.task_permissions)), q.freshness_requirement, version)
        return hashlib.sha256(repr(material).encode()).hexdigest()
    def get(self, key): return deepcopy(self._items.get(key))
    def put(self, key, package): self._items[key] = deepcopy(package)
    def clear(self): self._items.clear()

class RetrievalEngine:
    def __init__(self, embedding_provider: EmbeddingProvider | None=None,
                 vector_store: VectorStore | None=None):
        self.embedding = embedding_provider or MockEmbeddingProvider()
        self.vector_store = vector_store or InMemoryVectorStore()
        self.records: dict[str, RetrievalResult] = {}; self.cache = RetrievalCache(); self.version = 0
        self.query_log: list[dict] = []

    def index(self, result: RetrievalResult) -> None:
        if result.security_classification is SecurityScope.SYSTEM_SECRET:
            raise ValueError("SYSTEM_SECRET is excluded from all retrieval indexes")
        self.records[result.result_id] = result
        vector = self.embedding.embed_text(f"{result.title} {result.relevant_passage}")
        self.vector_store.upsert(VectorRecord(result.result_id, result.source_type, result.source_id,
            result.result_id, self.embedding.version,
            hashlib.sha256(result.relevant_passage.encode()).hexdigest(), vector,
            {"security_scope": result.security_classification.value, "result_id": result.result_id}))
        self.version += 1; self.cache.clear()

    def plan(self, query: RetrievalQuery) -> SearchPlan:
        query.normalized_query = normalize_query(query.raw_query)
        if not query.domains: query.domains = self.select_domains(query.normalized_query)
        why = any(word in query.normalized_query for word in ("why", "почему", "relationship", "dependency"))
        modes = [Mode.KEYWORD, Mode.SEMANTIC, Mode.HYBRID] + ([Mode.GRAPH] if why else [])
        if query.time_range or query.freshness_requirement: modes.append(Mode.TIME_AWARE)
        return SearchPlan(["records", "vectors"] + (["graph"] if why else []), modes,
                          max(query.result_limit * 4, 20), 2 if why else 0)

    @staticmethod
    def select_domains(query: str) -> set[Domain]:
        mapping = {Domain.DECISIONS:("why", "decision", "почему", "решен"),
                   Domain.RESEARCH:("research", "study", "исслед"),
                   Domain.CONTENT:("post", "content", "publish", "контент"),
                   Domain.AGENTS:("agent", "агент"), Domain.WORKFLOWS:("workflow", "plan", "task"),
                   Domain.AI_TOOLS:("tool", "model", "ai"), Domain.MEMORY:("remember", "memory", "ago")}
        selected = {domain for domain, words in mapping.items() if any(w in query for w in words)}
        return selected or {Domain.PROJECT, Domain.MEMORY, Domain.PUBLIC_KNOWLEDGE}

    def search(self, query: RetrievalQuery, *, min_confidence=0.0) -> RetrievalPackage:
        started = time.monotonic(); plan = self.plan(query); trace = RetrievalTrace(plan.stores, plan.modes)
        cache_key = self.cache.key(query, self.version); cached = self.cache.get(cache_key)
        if cached: cached.trace.cache_hit = True; return cached
        permitted = allowed_scopes(query); tokens = set(query.normalized_query.split())
        candidates: dict[str, RetrievalResult] = {}
        # Security and domain predicates run before either lexical or vector candidate collection.
        for record in self.records.values():
            if not may_access(query, record.security_classification):
                trace.excluded[record.result_id] = "permission denied"; continue
            if query.domains and record.domain not in query.domains: continue
            words = set(normalize_query(record.title+" "+record.relevant_passage).split())
            lexical = len(tokens & words) / max(len(tokens), 1)
            if lexical: record.keyword_score = lexical; candidates[record.result_id] = deepcopy(record)
        for vector, similarity in self.vector_store.search(self.embedding.embed_text(query.normalized_query),
                                                            plan.candidate_limit, permitted):
            record = self.records.get(vector.metadata["result_id"])
            if not record or (query.domains and record.domain not in query.domains): continue
            item = candidates.setdefault(record.result_id, deepcopy(record)); item.semantic_score=max(0, similarity)
        trace.candidates_found = len(candidates)
        filtered = []
        for item in candidates.values():
            reason = self._exclude_reason(query, item, min_confidence)
            if reason: trace.excluded[item.result_id] = reason
            else: filtered.append(item)
        selected = deduplicate(rank(filtered))[:query.result_limit]
        for item in selected: trace.selected_reasons[item.result_id] = f"hybrid score {item.score:.3f}"
        conflicts = self._conflicts(selected); trace.conflicts_detected = len(conflicts)
        context, estimate = self.build_context(selected, conflicts, token_budget=2000)
        missing = None if selected else MissingStatus.INSUFFICIENT_KNOWLEDGE
        package = RetrievalPackage(query, query.intent, selected,
            "; ".join(item.summary for item in selected),
            sum(x.confidence for x in selected)/len(selected) if selected else 0.0,
            conflicts, missing, "Research" if missing else None, context, estimate, trace)
        self.cache.put(cache_key, package)
        self.query_log.append({"query_id":query.query_id,"requester":query.requester,
            "domains":[d.value for d in query.domains],"result_count":len(selected),
            "latency_ms":round((time.monotonic()-started)*1000,2),"selected":[x.result_id for x in selected]})
        return package

    retrieve = search
    def retrieve_by_id(self, result_id: str, query: RetrievalQuery):
        item=self.records.get(result_id)
        return deepcopy(item) if item and may_access(query,item.security_classification) else None
    def retrieve_related(self, result_id, query):
        item=self.retrieve_by_id(result_id,query)
        return [self.retrieve_by_id(x,query) for x in item.relationships if self.retrieve_by_id(x,query)] if item else []
    def retrieve_history(self, source_id, query):
        return sorted((deepcopy(x) for x in self.records.values() if x.source_id==source_id and may_access(query,x.security_classification)), key=lambda x:x.valid_from or datetime.min.replace(tzinfo=timezone.utc))
    def retrieve_conflicts(self, query): return self.search(query).conflicts
    def explain_retrieval(self, query): return self.search(query).trace

    @staticmethod
    def _exclude_reason(query, item, minimum):
        if item.confidence < minimum: return "below confidence threshold"
        if query.freshness_requirement and item.freshness_status != query.freshness_requirement: return "freshness mismatch"
        if query.time_range:
            date=item.valid_from or item.last_verified
            if date and query.time_range.after and date < query.time_range.after: return "before requested range"
            if date and query.time_range.before and date > query.time_range.before: return "after requested range"
        return None

    @staticmethod
    def _conflicts(items):
        groups={}
        for item in items:
            if claim:=item.metadata.get("claim_key"): groups.setdefault(claim,[]).append(item)
        output=[]
        for group in groups.values():
            values={x.metadata.get("claim_value") for x in group}
            if len(values)>1:
                a,b=next((a,b) for a in group for b in group if a.metadata.get("claim_value")!=b.metadata.get("claim_value"))
                output.append(Conflict(a.relevant_passage,[a.source_id],b.relevant_passage,[b.source_id],min(a.confidence,b.confidence),[d for d in (a.last_verified,b.last_verified) if d]))
        return output

    @staticmethod
    def build_context(items, conflicts=(), token_budget=2000):
        blocks=[]; used=0
        for item in items:
            block=f"[{item.source_id} v{item.version} | confidence={item.confidence:.2f} | {item.freshness_status}]\n{item.relevant_passage}"
            cost=max(1,len(block)//4)
            if used+cost>token_budget: continue
            blocks.append(block); used+=cost
        for conflict in conflicts:
            marker=f"CONFLICT ({conflict.resolution_status}): {conflict.claim_a} <> {conflict.claim_b}"
            if used+len(marker)//4<=token_budget: blocks.append(marker); used+=len(marker)//4
        return "\n\n".join(blocks), used
