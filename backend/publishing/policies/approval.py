from ..domain.models import *


class StrictApprovalValidator:
    def __init__(self, guardian: dict[str, Approval], founder: dict[str, Approval]):
        self.guardian, self.founder = guardian, founder

    def validate(self, publication: Publication, content: ContentSnapshot) -> None:
        g = self.guardian.get(publication.guardian_approval_id)
        f = self.founder.get(publication.founder_approval_id)
        for label, approval in (("Guardian", g), ("Founder", f)):
            if not approval or approval.status != ApprovalStatus.APPROVED:
                raise ValidationError(f"{label} approval is not valid")
            if (approval.content_id, approval.content_version) != (content.content_id, content.version):
                raise ValidationError(f"{label} approval does not match content version")
        if publication.content_version != content.version:
            raise ValidationError("publication content version changed after approval")
        if content.status != ContentStatus.READY_TO_PUBLISH:
            raise ValidationError("content is not ready to publish")
