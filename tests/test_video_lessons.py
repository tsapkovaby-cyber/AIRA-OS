from backend.learning.video import VideoLessonAsset, VideoLessonCatalog, reference_video_asset
from backend.learning.voice import FOUNDER_VOICE


def test_ready_video_delivers_playback_and_founder_voice_identity():
    catalog = VideoLessonCatalog()
    asset = catalog.register(reference_video_asset("lesson-1", target_language="de", explanation_language="ru"))
    delivery = catalog.delivery_for_lesson("lesson-1")
    assert delivery.available is True
    assert delivery.playback_url
    assert asset.target_language == "German"
    assert asset.explanation_language == "Russian"
    assert asset.voice_profile_id == FOUNDER_VOICE.id


def test_missing_video_has_safe_fallback():
    delivery = VideoLessonCatalog().delivery_for_lesson("missing")
    assert delivery.available is False
    assert "text lesson" in delivery.fallback_message


def test_processing_video_keeps_transcript_available():
    catalog = VideoLessonCatalog()
    asset = VideoLessonAsset("v1", "l1", "AIRA lesson", "es", "en", 300, transcript="Read me", status="processing")
    catalog.register(asset)
    delivery = catalog.delivery_for_lesson("l1")
    assert delivery.available is False
    assert delivery.transcript == "Read me"


def test_all_academy_languages_are_valid_for_video_metadata():
    for code in ("en", "ru", "es", "it", "tr", "kk", "fr", "de"):
        asset = reference_video_asset(f"lesson-{code}", target_language=code, explanation_language=code)
        assert asset.target_language
        assert asset.explanation_language


def test_invalid_duration_is_rejected():
    try:
        VideoLessonAsset("v", "l", "bad", "en", "ru", -1)
    except ValueError as exc:
        assert "duration" in str(exc)
    else:
        raise AssertionError("negative video duration must fail")
