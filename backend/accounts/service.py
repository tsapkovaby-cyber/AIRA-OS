from __future__ import annotations
from datetime import timedelta
from .models import AccountDeletionRequest, AccountRole, AccountStatus, Credential, EmailIdentity, RecoveryToken, Session, StudentAccountLink, UserAccount, new_id, now
from .security import PBKDF2PasswordHasher, new_token, token_digest

class AccountError(ValueError): pass
class AuthenticationFailed(AccountError): pass
class DuplicateEmail(AccountError): pass
class NotFound(AccountError): pass
class OwnershipDenied(AccountError): pass
class InvalidToken(AccountError): pass

class AccountService:
    def __init__(self, *, hasher=None, session_ttl=timedelta(days=30), token_ttl=timedelta(hours=1)):
        self.hasher=hasher or PBKDF2PasswordHasher(); self.session_ttl=session_ttl; self.token_ttl=token_ttl
        self.accounts={}; self.emails={}; self.credentials={}; self.sessions={}; self.tokens={}; self.links=[]; self.deletions={}
    @staticmethod
    def normalize_email(email:str)->str:return email.strip().casefold()
    def register_student_account(self,email:str,password:str)->UserAccount:
        normalized=self.normalize_email(email)
        if normalized in self.emails: raise DuplicateEmail("account unavailable")
        account=UserAccount(role=AccountRole.STUDENT); self.accounts[account.id]=account
        self.emails[normalized]=EmailIdentity(account.id,normalized); self.credentials[account.id]=Credential(account.id,self.hasher.hash(password)); return account
    def get_account(self,account_id:str)->UserAccount:
        try:return self.accounts[account_id]
        except KeyError:raise NotFound(account_id) from None
    def authenticate(self,email:str,password:str)->tuple[UserAccount,str]:
        identity=self.emails.get(self.normalize_email(email))
        if not identity: raise AuthenticationFailed("invalid credentials")
        account=self.get_account(identity.account_id)
        if account.status in {AccountStatus.DISABLED,AccountStatus.DELETED,AccountStatus.DELETION_REQUESTED}: raise AuthenticationFailed("invalid credentials")
        credential=self.credentials[account.id]
        if not self.hasher.verify(password,credential.password_hash): raise AuthenticationFailed("invalid credentials")
        account.last_login_at=now(); account.updated_at=now(); return account,self.create_session(account.id)
    def create_session(self,account_id:str)->str:
        self.get_account(account_id); raw=new_token(); session=Session(new_id(),account_id,token_digest(raw),now()+self.session_ttl); self.sessions[session.id]=session; return raw
    def validate_session(self,raw_token:str)->UserAccount:
        digest=token_digest(raw_token)
        for session in self.sessions.values():
            if hmac_compare(session.token_digest,digest):
                if session.revoked_at or session.expires_at<=now(): raise AuthenticationFailed("invalid session")
                account=self.get_account(session.account_id)
                if account.status not in {AccountStatus.ACTIVE,AccountStatus.PENDING_VERIFICATION}: raise AuthenticationFailed("invalid session")
                session.last_seen_at=now(); return account
        raise AuthenticationFailed("invalid session")
    get_current_account_from_session=validate_session
    def logout(self,raw_token:str)->None:
        digest=token_digest(raw_token)
        for session in self.sessions.values():
            if hmac_compare(session.token_digest,digest): session.revoked_at=now(); return
    revoke_session=logout
    def revoke_all_sessions(self,account_id:str)->None:
        for session in self.sessions.values():
            if session.account_id==account_id and not session.revoked_at: session.revoked_at=now()
    def change_password(self,account_id:str,current_password:str,new_password:str)->None:
        credential=self.credentials[self.get_account(account_id).id]
        if not self.hasher.verify(current_password,credential.password_hash): raise AuthenticationFailed("invalid credentials")
        credential.password_hash=self.hasher.hash(new_password); credential.updated_at=now(); self.revoke_all_sessions(account_id)
    def _issue_token(self,account_id:str,kind:str)->str:
        self.get_account(account_id); raw=new_token(); token=RecoveryToken(new_id(),account_id,kind,token_digest(raw),now()+self.token_ttl); self.tokens[token.id]=token; return raw
    def request_password_reset(self,email:str)->str|None:
        identity=self.emails.get(self.normalize_email(email)); return self._issue_token(identity.account_id,"password_reset") if identity else None
    def request_email_verification(self,account_id:str)->str:return self._issue_token(account_id,"email_verify")
    def _consume_token(self,raw_token:str,kind:str)->RecoveryToken:
        digest=token_digest(raw_token)
        for token in self.tokens.values():
            if token.kind==kind and hmac_compare(token.token_digest,digest):
                if token.consumed_at or token.expires_at<=now(): raise InvalidToken("invalid token")
                token.consumed_at=now(); return token
        raise InvalidToken("invalid token")
    def reset_password(self,raw_token:str,new_password:str)->None:
        token=self._consume_token(raw_token,"password_reset"); credential=self.credentials[token.account_id]; credential.password_hash=self.hasher.hash(new_password); credential.updated_at=now(); self.revoke_all_sessions(token.account_id)
    consume_password_recovery_token=reset_password
    def verify_email(self,raw_token:str)->None:
        token=self._consume_token(raw_token,"email_verify"); account=self.get_account(token.account_id)
        for identity in self.emails.values():
            if identity.account_id==account.id: identity.verified=True; identity.verified_at=now(); break
        account.status=AccountStatus.ACTIVE; account.updated_at=now()
    def create_student_link(self,account_id:str,student_id:str,*,relationship="owner",primary=True)->StudentAccountLink:
        self.get_account(account_id)
        for link in self.links:
            if link.student_id==student_id and link.account_id!=account_id: raise OwnershipDenied("student already owned")
        link=StudentAccountLink(account_id,student_id,relationship,primary); self.links.append(link); return link
    def get_primary_student(self,account_id:str)->str:
        self.get_account(account_id)
        for link in self.links:
            if link.account_id==account_id and link.primary:return link.student_id
        raise NotFound("primary student")
    def assert_student_owner(self,account_id:str,student_id:str)->None:
        if not any(l.account_id==account_id and l.student_id==student_id for l in self.links): raise OwnershipDenied("student access denied")
    def disable_account(self,account_id:str)->None:
        account=self.get_account(account_id); account.status=AccountStatus.DISABLED; account.updated_at=now(); self.revoke_all_sessions(account_id)
    def request_account_deletion(self,account_id:str)->AccountDeletionRequest:
        account=self.get_account(account_id); account.status=AccountStatus.DELETION_REQUESTED; account.updated_at=now(); self.revoke_all_sessions(account_id); request=AccountDeletionRequest(account_id); self.deletions[account_id]=request; return request
    def complete_account_deletion(self,account_id:str)->None:
        account=self.get_account(account_id); account.status=AccountStatus.DELETED; account.updated_at=now(); self.credentials.pop(account_id,None); request=self.deletions.setdefault(account_id,AccountDeletionRequest(account_id)); request.completed_at=now(); self.revoke_all_sessions(account_id)

def hmac_compare(a:str,b:str)->bool:
    import hmac
    return hmac.compare_digest(a,b)
