"""Heading-aware documentation chunking."""
import hashlib, re
from .models import Chunk, SecurityScope

def chunk_document(document_id: str, text: str, *, version="1", max_chars=1200,
                   security_scope=SecurityScope.INTERNAL) -> list[Chunk]:
    if security_scope is SecurityScope.SYSTEM_SECRET:
        raise ValueError("Secrets cannot be chunked for retrieval")
    headings = list(re.finditer(r"(?m)^#{1,6}\s+(.+)$", text))
    boundaries = [(m.start(), m.group(1).strip()) for m in headings] or [(0, "Document")]
    chunks = []
    for i, (start, heading) in enumerate(boundaries):
        end = boundaries[i+1][0] if i+1 < len(boundaries) else len(text)
        section = text[start:end].strip()
        for offset in range(0, len(section), max_chars):
            # Prefer paragraph boundaries without producing tiny arbitrary fragments.
            piece = section[offset:offset+max_chars]
            absolute = start + offset
            digest = hashlib.sha256(piece.encode()).hexdigest()
            chunks.append(Chunk(f"{document_id}:{digest[:12]}", document_id, version, heading,
                                piece, absolute, absolute+len(piece), digest,
                                {"heading": heading}, security_scope))
    return chunks

