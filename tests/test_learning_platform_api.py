import pytest
from backend.accounts.service import AccountService
from backend.learning.seeds import conversational_english_a1
from backend.learning.service import LearningPlatformService
from backend.learning_api import LearningPlatformAPI, APIError, Unauthorized

def platform():
    learning=LearningPlatformService();learning.create_course(conversational_english_a1());accounts=AccountService();return LearningPlatformAPI(accounts,learning),accounts,learning

def test_register_login_profile_catalog_and_learning_flow():
    api,_,_=platform();registered=api.register("Learner@Example.COM","correct horse battery staple");login=api.login("learner@example.com","correct horse battery staple");token=login["session_token"]
    assert registered["account_id"]==login["account_id"];assert api.get_profile(token)["student_id"]==registered["student_id"]
    profile=api.update_profile(token,native_language="Russian",target_languages=["English"],current_level="A1");assert profile["current_level"]=="A1"
    courses=api.list_courses(token);course_id=courses[0]["id"];api.enroll(token,course_id);lesson=api.next_lesson(token,course_id);api.start_lesson(token,course_id,lesson["id"]);api.complete_lesson(token,course_id,lesson["id"]);assert api.course_progress(token,course_id)["completion_percentage"]==50.0

def test_logout_invalidates_api_session():
    api,_,_=platform();api.register("a@example.com","correct horse battery staple");token=api.login("a@example.com","correct horse battery staple")["session_token"];api.logout(token)
    with pytest.raises(Unauthorized):api.list_courses(token)

def test_profile_rejects_arbitrary_fields():
    api,_,_=platform();api.register("b@example.com","correct horse battery staple");token=api.login("b@example.com","correct horse battery staple")["session_token"]
    with pytest.raises(APIError):api.update_profile(token,is_admin=True)

def test_accounts_cannot_address_another_student_through_api():
    api,accounts,_=platform();one=api.register("one@example.com","correct horse battery staple");two=api.register("two@example.com","correct horse battery staple");token=api.login("one@example.com","correct horse battery staple")["session_token"]
    assert accounts.get_primary_student(api.current_account(token).id)==one["student_id"] and one["student_id"]!=two["student_id"]
    assert api.get_profile(token)["student_id"]==one["student_id"]

def test_tutor_session_is_owned_by_authenticated_student():
    api,_,_=platform();registered=api.register("tutor@example.com","correct horse battery staple");token=api.login("tutor@example.com","correct horse battery staple")["session_token"];session=api.start_tutor_session(token);assert session["student_id"]==registered["student_id"]
