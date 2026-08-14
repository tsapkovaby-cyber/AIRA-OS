"""Provider-neutral AIRA video lesson metadata and delivery rules.

Large media, founder voice masters, avatar source footage, and provider secrets
must live outside GitHub. The repository stores only safe metadata and external
asset identifiers/URLs supplied by deployment or a media backend.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from .languages import get_language
from .voice import FOUNDER_VOICE

@dataclass(frozen=True, slots=True)
class SubtitleTrack:
    language: str
    url: str
    kind: str = "subtitles"

@dataclass(slots=True)
class VideoLessonAsset:
    id: str
    lesson_id: str
    title: str
    target_language: str
    explanation_language: str
    duration_seconds: int
    playback_url: str | None = None
    poster_url: str | None = None
    transcript: str = ""
    subtitle_tracks: list[SubtitleTrack] = field(default_factory=list)
    voice_profile_id: str = FOUNDER_VOICE.id
    status: str = "ready"

    def __post_init__(self) -> None:
        self.target_language = get_language(self.target_language).name
        self.explanation_language = get_language(self.explanation_language).name
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        if self.status not in {"draft", "processing", "ready", "unavailable"}:
            raise ValueError(f"unsupported video status: {self.status}")

@dataclass(frozen=True, slots=True)
class VideoDelivery:
    available: bool
    playback_url: str | None
    poster_url: str | None
    transcript: str
    subtitle_tracks: tuple[SubtitleTrack, ...]
    fallback_message: str | None = None

class VideoLessonCatalog:
    """In-memory MVP catalog; production storage can implement the same behavior."""
    def __init__(self) -> None:
        self._by_lesson: dict[str, VideoLessonAsset] = {}

    def register(self, asset: VideoLessonAsset) -> VideoLessonAsset:
        self._by_lesson[asset.lesson_id] = asset
        return asset

    def get_for_lesson(self, lesson_id: str) -> VideoLessonAsset | None:
        return self._by_lesson.get(lesson_id)

    def delivery_for_lesson(self, lesson_id: str) -> VideoDelivery:
        asset = self.get_for_lesson(lesson_id)
        if asset is None:
            return VideoDelivery(False, None, None, "", (), "Video lesson is not published yet. Continue with the text lesson and AIRA Tutor.")
        if asset.status != "ready" or not asset.playback_url:
            return VideoDelivery(False, None, asset.poster_url, asset.transcript, tuple(asset.subtitle_tracks), "Video is temporarily unavailable. Transcript and lesson activities remain available.")
        return VideoDelivery(True, asset.playback_url, asset.poster_url, asset.transcript, tuple(asset.subtitle_tracks))


def reference_video_asset(lesson_id: str, *, target_language: str = "en", explanation_language: str = "ru") -> VideoLessonAsset:
    """Safe reference metadata used by tests/demos; it contains no real master media."""
    return VideoLessonAsset(
        id=f"video-{lesson_id}",
        lesson_id=lesson_id,
        title="AIRA video lesson",
        target_language=target_language,
        explanation_language=explanation_language,
        duration_seconds=480,
        playback_url=f"https://media.example.invalid/{lesson_id}/master.m3u8",
        poster_url=f"https://media.example.invalid/{lesson_id}/poster.jpg",
        transcript="Reference transcript for the AIRA lesson.",
        subtitle_tracks=[SubtitleTrack(explanation_language, f"https://media.example.invalid/{lesson_id}/subtitles.vtt")],
    )
