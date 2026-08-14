"""Vector store abstraction and scope-filtered in-memory adapter."""
from abc import ABC, abstractmethod
import math
from .models import SecurityScope, VectorRecord

class VectorStore(ABC):
    @abstractmethod
    def upsert(self, record: VectorRecord) -> None: ...
    @abstractmethod
    def search(self, vector: list[float], limit: int, allowed_scopes: set[SecurityScope]) -> list[tuple[VectorRecord, float]]: ...
    @abstractmethod
    def delete(self, vector_id: str) -> None: ...

class InMemoryVectorStore(VectorStore):
    def __init__(self): self.records: dict[str, VectorRecord] = {}
    def upsert(self, record: VectorRecord) -> None:
        if record.metadata.get("security_scope") == SecurityScope.SYSTEM_SECRET.value:
            raise ValueError("SYSTEM_SECRET records must never be embedded")
        self.records[record.vector_id] = record
    def search(self, vector, limit, allowed_scopes):
        def cosine(other):
            denominator = math.sqrt(sum(x*x for x in vector))*math.sqrt(sum(x*x for x in other))
            return sum(a*b for a,b in zip(vector, other))/denominator if denominator else 0.0
        safe = (record for record in self.records.values()
                if SecurityScope(record.metadata.get("security_scope", "INTERNAL")) in allowed_scopes)
        return sorted(((record, cosine(record.vector)) for record in safe), key=lambda x: x[1], reverse=True)[:limit]
    def delete(self, vector_id): self.records.pop(vector_id, None)

