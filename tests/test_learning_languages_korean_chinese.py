from backend.learning.languages import explanation_languages, get_language, learning_languages
from backend.learning.voice import VoiceTutorService


def test_catalog_contains_ten_learning_languages():
    codes = [language.code for language in learning_languages()]
    assert len(codes) == 10
    assert "ko" in codes
    assert "zh" in codes


def test_korean_metadata():
    korean = get_language("ko")
    assert korean.name == "Korean"
    assert korean.native_name == "한국어"
    assert korean.writing_system == "Hangul"


def test_mandarin_aliases_and_simplified_script():
    mandarin = get_language("zh")
    assert mandarin.name == "Mandarin Chinese"
    assert mandarin.native_name == "简体中文"
    assert mandarin.writing_system == "Simplified Chinese"
    assert get_language("Chinese") is mandarin
    assert get_language("Mandarin") is mandarin


def test_korean_and_mandarin_are_available_as_explanation_languages():
    codes = {language.code for language in explanation_languages()}
    assert {"ko", "zh"}.issubset(codes)


def test_voice_tutor_accepts_new_languages_for_target_and_explanation():
    tutor = VoiceTutorService()
    korean = tutor.practice_turn(student_id="s1", audio="안녕하세요".encode(), target_language="ko", explanation_language="ru")
    chinese = tutor.practice_turn(student_id="s2", audio="你好".encode(), target_language="zh", explanation_language="en")
    assert korean.target_language == "Korean"
    assert chinese.target_language == "Mandarin Chinese"
