from backend.accounts.service import AccountService
from backend.learning.languages import get_language, learning_languages, resolve_explanation_language
from backend.learning.seeds import multilingual_language_catalog
from backend.learning.service import LearningPlatformService
from backend.learning_api.service import LearningPlatformAPI


def api_setup():
    learning = LearningPlatformService()
    for course in multilingual_language_catalog(("A1",)):
        learning.create_course(course)
    api = LearningPlatformAPI(AccountService(), learning)
    api.register("learner@example.com", "correct horse battery staple")
    token = api.login("learner@example.com", "correct horse battery staple")["session_token"]
    return api, token


def test_ten_learning_languages_include_russian_korean_and_mandarin():
    names = {language.name for language in learning_languages()}
    assert names == {"English", "Russian", "Spanish", "Italian", "Turkish", "Kazakh", "French", "German", "Korean", "Mandarin Chinese"}


def test_russian_can_be_target_and_explanation_language():
    assert get_language("ru").name == "Russian"
    assert resolve_explanation_language("Russian", None) == "Russian"
    assert resolve_explanation_language("English", "Russian") == "Russian"


def test_app_language_follows_explanation_language():
    api, token = api_setup()
    profile = api.update_profile(token, native_language="English", explanation_language="Russian", target_languages=["German"])
    assert profile["explanation_language"] == "Russian"
    assert profile["app_language"] == "Russian"
    assert api.app_language(token) == "Russian"


def test_native_language_becomes_default_explanation_and_app_language():
    api, token = api_setup()
    profile = api.update_profile(token, native_language="Turkish", target_languages=["English"])
    assert profile["explanation_language"] == "Turkish"
    assert profile["app_language"] == "Turkish"


def test_catalog_has_course_shell_for_each_language():
    courses = multilingual_language_catalog(("A1",))
    assert {course.language for course in courses} == {language.name for language in learning_languages()}
