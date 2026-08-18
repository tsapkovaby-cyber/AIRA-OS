export type LearnerProfile = {
  nativeLanguage: string;
  targetLanguage: string;
  currentLevel: string;
  targetLevel: string;
  learningGoals: string;
  dailyTarget: number;
  completedLessons: string[];
  streak: number;
  lastActivityAt: string | null;
};

export const DEFAULT_LEARNER_PROFILE: LearnerProfile = {
  nativeLanguage: "Russian",
  targetLanguage: "English",
  currentLevel: "A1",
  targetLevel: "B1",
  learningGoals: "Speak confidently in everyday conversations",
  dailyTarget: 20,
  completedLessons: [],
  streak: 0,
  lastActivityAt: null,
};

const STORAGE_KEY = "aira.learner.profile.v1";
const STUDENT_KEY = "aira.learner.student-id.v1";

function studentId() {
  if (typeof window === "undefined") return "server";
  let id = window.localStorage.getItem(STUDENT_KEY);
  if (!id) {
    id = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `student-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    window.localStorage.setItem(STUDENT_KEY, id);
  }
  return id;
}

function syncProfile(profile: LearnerProfile) {
  if (typeof window === "undefined") return;
  void fetch("/api/learn/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: studentId(), learningLanguage: profile.targetLanguage, level: profile.currentLevel, streak: profile.streak, completedLessons: profile.completedLessons.length, lastActiveAt: profile.lastActivityAt, accessStatus: "active", profile }) }).catch(() => undefined);
}

function recordLessonCompleted(profile: LearnerProfile, lessonId: string) {
  if (typeof window === "undefined") return;
  void fetch("/api/learn/events", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ studentId: studentId(), type: "lesson_completed", language: profile.targetLanguage, level: profile.currentLevel, lessonId }) }).catch(() => undefined);
}

export function loadLearnerProfile(): LearnerProfile {
  if (typeof window === "undefined") return DEFAULT_LEARNER_PROFILE;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_LEARNER_PROFILE;
    return { ...DEFAULT_LEARNER_PROFILE, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_LEARNER_PROFILE;
  }
}

export function saveLearnerProfile(profile: LearnerProfile) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
  syncProfile(profile);
}

export async function hydrateLearnerProfileFromAccount() {
  if (typeof window === "undefined") return null;
  try {
    const res = await fetch("/api/learn/profile", { cache: "no-store" });
    if (!res.ok) return null;
    const data = await res.json();
    if (!data.profile) return null;
    const profile = { ...DEFAULT_LEARNER_PROFILE, ...data.profile } as LearnerProfile;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    if (data.user?.id) window.localStorage.setItem(STUDENT_KEY, data.user.id);
    return profile;
  } catch {
    return null;
  }
}

export function markLessonComplete(lessonId: string) {
  const profile = loadLearnerProfile();
  const isNew = !profile.completedLessons.includes(lessonId);
  const completedLessons = isNew ? [...profile.completedLessons, lessonId] : profile.completedLessons;
  const next = { ...profile, completedLessons, streak: Math.max(profile.streak, 1), lastActivityAt: new Date().toISOString() };
  saveLearnerProfile(next);
  if (isNew) recordLessonCompleted(next, lessonId);
  return next;
}
