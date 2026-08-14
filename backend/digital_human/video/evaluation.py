"""Explainable timeline evaluation: safety dimensions remain separate."""
from dataclasses import dataclass
from .models import ArtifactType, VideoArtifact, VideoIdentityLock, VideoStatus

@dataclass(frozen=True)
class TemporalIdentityResult:
    temporal_identity_score: float; minimum_score: float; frame_scores: tuple[tuple[int, float], ...]
    artifacts: tuple[VideoArtifact, ...]; passed: bool

def evaluate_temporal_identity(frame_scores: list[tuple[int, float]], lock: VideoIdentityLock, fps: float=30) -> TemporalIdentityResult:
    if not frame_scores or fps <= 0: raise ValueError("sampled frame scores and positive fps required")
    values=[value for _, value in frame_scores]
    for value in values:
        if not 0 <= value <= 100: raise ValueError("frame score outside 0..100")
    peak=values[0]; artifacts=[]
    for (frame, value) in frame_scores:
        peak=max(peak, value)
        if value < lock.minimum_identity_score or peak-value > lock.maximum_frame_drop:
            artifacts.append(VideoArtifact(ArtifactType.IDENTITY_DRIFT, frame/fps, (frame, frame),
                                           int(min(100, max(lock.minimum_identity_score-value, peak-value)*10)),
                                           "identity score threshold/drop", motion_state="sampled"))
    # Penalize local collapse so a high average cannot hide one wrong frame.
    temporal=min(sum(values)/len(values), min(values)+lock.maximum_frame_drop)
    return TemporalIdentityResult(temporal, min(values), tuple(frame_scores), tuple(artifacts), not artifacts)

@dataclass(frozen=True)
class LipSyncResult:
    lip_timing_accuracy: float; phoneme_match: float; pause_match: float; jaw_stability: float
    lip_shape_naturalness: float; face_identity_preservation: float; audio_delay_ms: float; visual_delay_ms: float
    passed: bool; failures: tuple[str, ...]

def evaluate_lipsync(*, lip_timing_accuracy: float, phoneme_match: float, pause_match: float,
                     jaw_stability: float, lip_shape_naturalness: float, face_identity_preservation: float,
                     audio_delay_ms: float, visual_delay_ms: float, threshold: float=85) -> LipSyncResult:
    metrics=(lip_timing_accuracy, phoneme_match, pause_match, jaw_stability, lip_shape_naturalness, face_identity_preservation)
    if any(not 0 <= metric <= 100 for metric in metrics): raise ValueError("lip-sync metrics outside 0..100")
    failures=[]
    if lip_timing_accuracy < threshold or abs(audio_delay_ms-visual_delay_ms) > 80: failures.append("OUT_OF_SYNC")
    if phoneme_match < threshold: failures.append("PHONEME_ERROR")
    if jaw_stability < threshold: failures.append("JAW_ARTIFACT")
    if face_identity_preservation < threshold: failures.append("FACE_DRIFT")
    return LipSyncResult(*metrics, audio_delay_ms, visual_delay_ms, not failures, tuple(failures))

@dataclass(frozen=True)
class MotionResult:
    naturalness: float; continuity: float; eye_behavior: float; hand_quality: float; passed: bool

def evaluate_motion(naturalness: float, continuity: float, eye_behavior: float, hand_quality: float, threshold=80):
    values=(naturalness, continuity, eye_behavior, hand_quality)
    if any(not 0 <= x <= 100 for x in values): raise ValueError("motion metrics outside 0..100")
    return MotionResult(*values, min(values) >= threshold)
