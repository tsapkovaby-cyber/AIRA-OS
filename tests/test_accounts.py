from datetime import timedelta
import pytest
from backend.accounts.models import AccountStatus
from backend.accounts.service import AccountService, AuthenticationFailed, DuplicateEmail, InvalidToken, OwnershipDenied
from backend.learning.service import LearningPlatformService

def test_registration_normalization_and_password_hashing():
    s=AccountService(); account=s.register_student_account(" User@Example.COM ","correct horse battery")
    assert "user@example.com" in s.emails and "correct horse battery" not in s.credentials[account.id].password_hash
    with pytest.raises(DuplicateEmail): s.register_student_account("user@example.com","another password")

def test_auth_sessions_revocation_and_password_change():
    s=AccountService(); a=s.register_student_account("u@example.com","old password"); a.status=AccountStatus.ACTIVE
    account,t1=s.authenticate("U@example.com","old password"); t2=s.create_session(a.id); assert account.id==a.id and s.validate_session(t1).id==a.id and s.validate_session(t2).id==a.id
    s.change_password(a.id,"old password","new password")
    with pytest.raises(AuthenticationFailed): s.validate_session(t1)
    _,t3=s.authenticate("u@example.com","new password"); s.logout(t3)
    with pytest.raises(AuthenticationFailed): s.validate_session(t3)

def test_wrong_password_disabled_and_deleted_rejected():
    s=AccountService(); a=s.register_student_account("u@example.com","right password")
    with pytest.raises(AuthenticationFailed): s.authenticate("u@example.com","wrong password")
    s.disable_account(a.id)
    with pytest.raises(AuthenticationFailed): s.authenticate("u@example.com","right password")
    a.status=AccountStatus.ACTIVE; s.request_account_deletion(a.id); s.complete_account_deletion(a.id)
    with pytest.raises(AuthenticationFailed): s.authenticate("u@example.com","right password")

def test_session_and_token_expiry_and_single_use():
    s=AccountService(session_ttl=timedelta(seconds=-1),token_ttl=timedelta(hours=1)); a=s.register_student_account("u@example.com","right password"); a.status=AccountStatus.ACTIVE
    raw=s.create_session(a.id)
    with pytest.raises(AuthenticationFailed): s.validate_session(raw)
    token=s.request_password_reset("u@example.com"); assert token
    s.reset_password(token,"new password")
    with pytest.raises(InvalidToken): s.reset_password(token,"another password")

def test_email_verification_single_use():
    s=AccountService(); a=s.register_student_account("u@example.com","right password"); token=s.request_email_verification(a.id); s.verify_email(token); assert a.status==AccountStatus.ACTIVE
    with pytest.raises(InvalidToken): s.verify_email(token)

def test_student_ownership_and_learning_integration():
    accounts=AccountService(); learning=LearningPlatformService(); a1=accounts.register_student_account("a@example.com","right password"); a2=accounts.register_student_account("b@example.com","right password"); student=learning.create_student(); accounts.create_student_link(a1.id,student.id)
    assert accounts.get_primary_student(a1.id)==student.id; accounts.assert_student_owner(a1.id,student.id)
    with pytest.raises(OwnershipDenied): accounts.assert_student_owner(a2.id,student.id)
    with pytest.raises(OwnershipDenied): accounts.create_student_link(a2.id,student.id)

def test_raw_session_token_is_not_stored():
    s=AccountService(); a=s.register_student_account("u@example.com","right password"); token=s.create_session(a.id); assert all(sess.token_digest!=token for sess in s.sessions.values())
