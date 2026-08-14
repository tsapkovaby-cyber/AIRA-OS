from backend.learning.voice import FOUNDER_VOICE, TEST_VOICE, VoiceTutorService


def test_voice_turn_keeps_target_and_explanation_languages_separate():
    tutor = VoiceTutorService()
    turn = tutor.practice_turn(student_id="s1", audio="Hola, un café por favor".encode(), target_language="es", explanation_language="ru")
    assert turn.target_language == "Spanish"
    assert turn.explanation_language == "Russian"
    assert turn.transcript == "Hola, un café por favor"
    assert "Russian" in turn.tutor_text


def test_ci_uses_test_voice_without_external_calls():
    turn = VoiceTutorService().practice_turn(student_id="s1", audio=b"Hello", target_language="en", explanation_language="en")
    assert turn.voice_profile_id == TEST_VOICE.id
    assert turn.audio_reference.startswith("test-audio://aira-test/")


def test_production_mode_selects_founder_voice_profile():
    turn = VoiceTutorService().practice_turn(student_id="s1", audio=b"Hello", target_language="en", explanation_language="ru", test_mode=False)
    assert turn.voice_profile_id == FOUNDER_VOICE.id
    assert turn.audio_reference.startswith("test-audio://aira-founder/")


def test_all_supported_languages_can_be_used_for_voice_practice():
    tutor = VoiceTutorService()
    for language in ("en", "ru", "es", "it", "tr", "kk", "fr", "de"):
        turn = tutor.practice_turn(student_id="s1", audio=b"practice", target_language=language, explanation_language=language)
        assert turn.transcript == "practice"
