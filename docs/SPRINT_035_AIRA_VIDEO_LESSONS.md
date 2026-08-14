# Sprint 035 — AIRA Video Lessons

## Goal
Add a safe, provider-neutral video lesson layer for AIRA Academy without storing large or sensitive media assets in GitHub.

## Model
Each video asset is linked to one lesson and stores metadata only: target language, explanation language, duration, playback reference, poster reference, transcript, subtitles, status, and the AIRA voice-profile identifier.

The default production voice identity is the Founder Voice introduced in Sprint 034 so AIRA keeps one recognizable voice across spoken practice and video lessons.

## Delivery and fallback
A ready asset with a playback URL can be played. Missing, processing, or unavailable media never blocks the lesson: the transcript, text lesson, exercises, and AIRA Tutor remain usable.

## Multilingual behavior
Target language and explanation language remain independent. The same video-lesson architecture supports English, Russian, Spanish, Italian, Turkish, Kazakh, French, and German. Subtitle tracks may be added independently per supported explanation language.

## Media security
Do not commit video masters, founder voice masters, raw avatar/source footage, cloned voice models, lip-sync source material, private CDN tokens, media signing keys, or provider credentials to GitHub.

Production media should live in private object/media storage or a streaming provider. GitHub should contain only safe metadata, provider-neutral code, documentation, and tests. Signed playback URLs should be generated server-side when protected access is introduced.

## Future work
Later sprints can add real media storage/CDN adapters, signed URLs, transcoding, subtitle generation, video progress checkpoints, entitlement checks by subscription plan, analytics, and an authoring pipeline for producing AIRA lessons from approved scripts.
