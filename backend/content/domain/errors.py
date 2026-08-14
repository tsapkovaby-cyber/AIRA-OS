class ContentError(ValueError):
    """Base domain validation error."""


class InvalidTransition(ContentError):
    pass


class EvidenceError(ContentError):
    pass


class ApprovalError(ContentError):
    pass
