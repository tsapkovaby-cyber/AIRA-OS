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
}

export function markLessonComplete(lessonId: string) {
  const profile = loadLearnerProfile();
  const completedLessons = profile.completedLessons.includes(lessonId)
    ? profile.completedLessons
    : [...profile.completedLessons, lessonId];
  const next = {
    ...profile,
    completedLessons,
    streak: Math.max(profile.streak, 1),
    lastActivityAt: new Date().toISOString(),
  };
  saveLearnerProfile(next);
  return next;
}
