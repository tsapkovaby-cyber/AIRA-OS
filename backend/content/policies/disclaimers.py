from ..domain.enums import ClaimKind
from ..domain.models import EvidenceClaim


def assign_disclaimer(claims: tuple[EvidenceClaim, ...], *, commercial: bool = False,
                      affiliate: bool = False) -> str | None:
    labels: list[str] = []
    if commercial:
        labels.append("Commercial content")
    if affiliate:
        labels.append("Affiliate relationship")
    if any(c.kind is ClaimKind.TEST_RESULT for c in claims):
        labels.append("Experimental result")
    if any(c.kind is ClaimKind.UNVERIFIED_INFORMATION for c in claims):
        labels.append("Unverified information")
    if any(c.kind is ClaimKind.AIRA_OPINION for c in claims):
        labels.append("AIRA opinion")
    return "; ".join(labels) or None
