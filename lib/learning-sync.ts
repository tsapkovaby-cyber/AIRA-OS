import type { LearnerProfile } from "./learner-profile";

const STUDENT_KEY = "aira.learner.student-id.v1";

export function getOrCreateStudentId() {
  if (typeof window === "undefined") return "server";
  let id = window.localStorage.getItem(STUDENT_KEY);
  if (!id) {
    id = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `student-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    window.localStorage.setItem(STUDENT_KEY, id);
  }
  return id;
}

export async function syncLearnerProfile(profile: LearnerProfile) {
  const id = getOrCreateStudentId();
  try {
    await fetch("/api/learn/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id, learningLanguage: profile.targetLanguage, level: profile.currentLevel, streak: profile.streak, completedLessons: profile.completedLessons.length, lastActiveAt: profile.lastActivityAt, accessStatus: "active" }) });
  } catch {}
}

export async function recordLearningEvent(type: "lesson_started"|"lesson_completed"|"practice_started"|"tutor_session"|"voice_session", data: { language?: string; level?: string; lessonId?: string } = {}) {
  try {
    await fetch("/api/learn/events", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ studentId: getOrCreateStudentId(), type, ...data }) });
  } catch {}
}
