"""Mandatory pre-retrieval authorization policy."""
from .models import RetrievalQuery, SecurityScope

def allowed_scopes(query: RetrievalQuery) -> set[SecurityScope]:
    scopes = {SecurityScope.PUBLIC, SecurityScope.INTERNAL}
    founder = query.requester.casefold() == "founder"
    delegated = SecurityScope.FOUNDER_PRIVATE in query.task_permissions
    if founder or delegated: scopes.add(SecurityScope.FOUNDER_PRIVATE)
    # SYSTEM_SECRET is deliberately impossible to authorize through RAG.
    return scopes

def may_access(query: RetrievalQuery, classification: SecurityScope) -> bool:
    return classification in allowed_scopes(query)

