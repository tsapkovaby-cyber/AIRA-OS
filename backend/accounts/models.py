from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

def now(): return datetime.now(timezone.utc)
def new_id(): return str(uuid4())

class AccountStatus(str, Enum):
    PENDING_VERIFICATION="pending_verification"; ACTIVE="active"; DISABLED="disabled"; DELETION_REQUESTED="deletion_requested"; DELETED="deleted"
class AccountRole(str, Enum):
    STUDENT="student"; PARENT="parent"; TEACHER="teacher"; ADMIN="admin"

@dataclass(slots=True)
class UserAccount:
    id:str=field(default_factory=new_id); status:AccountStatus=AccountStatus.PENDING_VERIFICATION; role:AccountRole=AccountRole.STUDENT
    created_at:datetime=field(default_factory=now); updated_at:datetime=field(default_factory=now); last_login_at:datetime|None=None
@dataclass(slots=True)
class EmailIdentity:
    account_id:str; email_normalized:str; verified:bool=False; verified_at:datetime|None=None
@dataclass(slots=True)
class Credential:
    account_id:str; password_hash:str; updated_at:datetime=field(default_factory=now)
@dataclass(slots=True)
class Session:
    id:str; account_id:str; token_digest:str; expires_at:datetime; created_at:datetime=field(default_factory=now); last_seen_at:datetime=field(default_factory=now); revoked_at:datetime|None=None
@dataclass(slots=True)
class RecoveryToken:
    id:str; account_id:str; kind:str; token_digest:str; expires_at:datetime; created_at:datetime=field(default_factory=now); consumed_at:datetime|None=None
@dataclass(slots=True)
class ExternalIdentity:
    account_id:str; provider:str; provider_user_id:str
@dataclass(slots=True)
class StudentAccountLink:
    account_id:str; student_id:str; relationship:str="owner"; primary:bool=True
@dataclass(slots=True)
class AccountDeletionRequest:
    account_id:str; requested_at:datetime=field(default_factory=now); completed_at:datetime|None=None
