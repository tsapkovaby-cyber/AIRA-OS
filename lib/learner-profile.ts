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

export type LearnerSyncState = {
  status: "local" | "syncing" | "synced" | "error";
  lastSyncedAt: string | null;
  accountLinked: boolean;
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
const SYNC_KEY = "aira.learner.sync.v1";
const SYNC_EVENT = "aira:learner-sync";

function studentId() {
  if (typeof window === "undefined") return "server";
  let id = window.localStorage.getItem(STUDENT_KEY);
  if (!id) {
    id = typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `student-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    window.localStorage.setItem(STUDENT_KEY, id);
  }
  return id;
}

export function loadLearnerSyncState(): LearnerSyncState {
  if (typeof window === "undefined") return { status: "local", lastSyncedAt: null, accountLinked: false };
  try {
    const raw = window.localStorage.getItem(SYNC_KEY);
    return raw ? { status: "local", lastSyncedAt: null, accountLinked: false, ...JSON.parse(raw) } : { status: "local", lastSyncedAt: null, accountLinked: false };
  } catch {
    return { status: "local", lastSyncedAt: null, accountLinked: false };
  }
}

function setLearnerSyncState(state: LearnerSyncState) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(SYNC_KEY, JSON.stringify(state));
  window.dispatchEvent(new CustomEvent(SYNC_EVENT, { detail: state }));
}

export function subscribeLearnerSyncState(listener: (state: LearnerSyncState) => void) {
  if (typeof window === "undefined") return () => undefined;
  const handler = (event: Event) => listener((event as CustomEvent<LearnerSyncState>).detail);
  window.addEventListener(SYNC_EVENT, handler);
  return () => window.removeEventListener(SYNC_EVENT, handler);
}

async function syncProfile(profile: LearnerProfile) {
  if (typeof window === "undefined") return;
  const previous = loadLearnerSyncState();
  setLearnerSyncState({ ...previous, status: "syncing" });
  try {
    const res = await fetch("/api/learn/profile", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: studentId(), learningLanguage: profile.targetLanguage, level: profile.currentLevel, streak: profile.streak, completedLessons: profile.completedLessons.length, lastActiveAt: profile.lastActivityAt, accessStatus: "active", profile }) });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.stored) {
      setLearnerSyncState({ status: data.accountLinked ? "error" : "local", lastSyncedAt: previous.lastSyncedAt, accountLinked: Boolean(data.accountLinked) });
      return;
    }
    setLearnerSyncState({ status: "synced", lastSyncedAt: new Date().toISOString(), accountLinked: Boolean(data.accountLinked) });
  } catch {
    setLearnerSyncState({ status: "error", lastSyncedAt: previous.lastSyncedAt, accountLinked: previous.accountLinked });
  }
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
  void syncProfile(profile);
}

export async function hydrateLearnerProfileFromAccount() {
  if (typeof window === "undefined") return null;
  try {
    const res = await fetch("/api/learn/profile", { cache: "no-store" });
    if (!res.ok) {
      setLearnerSyncState({ status: "local", lastSyncedAt: loadLearnerSyncState().lastSyncedAt, accountLinked: false });
      return null;
    }
    const data = await res.json();
    if (data.user?.id) window.localStorage.setItem(STUDENT_KEY, data.user.id);
    if (!data.profile) {
      setLearnerSyncState({ status: "local", lastSyncedAt: null, accountLinked: true });
      return null;
    }
    const profile = { ...DEFAULT_LEARNER_PROFILE, ...data.profile } as LearnerProfile;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    setLearnerSyncState({ status: "synced", lastSyncedAt: new Date().toISOString(), accountLinked: true });
    return profile;
  } catch {
    setLearnerSyncState({ status: "error", lastSyncedAt: loadLearnerSyncState().lastSyncedAt, accountLinked: loadLearnerSyncState().accountLinked });
    return null;
  }
}

export function clearLearnerAccountLink() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STUDENT_KEY);
  setLearnerSyncState({ status: "local", lastSyncedAt: null, accountLinked: false });
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
