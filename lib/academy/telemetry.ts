export type StudentRecord = {
  id: string;
  email?: string;
  displayName?: string;
  learningLanguage: string;
  level: string;
  streak: number;
  completedLessons: number;
  lastActiveAt?: string;
  createdAt?: string;
  accessStatus?: "active" | "trial" | "paused" | "blocked";
};

export type LearningEvent = {
  id: string;
  studentId: string;
  type: "lesson_started" | "lesson_completed" | "practice_started" | "tutor_session" | "voice_session";
  language?: string;
  level?: string;
  lessonId?: string;
  createdAt: string;
};

export type AcademyTelemetrySnapshot = {
  generatedAt?: string;
  students: StudentRecord[];
  events: LearningEvent[];
};

export type AcademyAnalytics = {
  source: "environment_snapshot" | "not_configured";
  generatedAt: string | null;
  totalStudents: number;
  activeToday: number;
  completedLessons: number;
  tutorSessions: number;
  voiceSessions: number;
  completionRate: number | null;
  topLanguage: string | null;
  topLevel: string | null;
  languages: Array<{ name: string; students: number }>;
  levels: Array<{ name: string; students: number }>;
};

function safeSnapshot(value: string | undefined): AcademyTelemetrySnapshot | null {
  if (!value) return null;
  try {
    const parsed = JSON.parse(value) as Partial<AcademyTelemetrySnapshot>;
    if (!Array.isArray(parsed.students) || !Array.isArray(parsed.events)) return null;
    return { generatedAt: parsed.generatedAt, students: parsed.students, events: parsed.events };
  } catch {
    return null;
  }
}

export function getAcademyTelemetrySnapshot(): AcademyTelemetrySnapshot {
  return safeSnapshot(process.env.AIRA_ACADEMY_TELEMETRY_JSON) ?? { students: [], events: [] };
}

function countBy(values: string[]) {
  const counts = new Map<string, number>();
  for (const value of values.filter(Boolean)) counts.set(value, (counts.get(value) ?? 0) + 1);
  return [...counts.entries()].map(([name, students]) => ({ name, students })).sort((a, b) => b.students - a.students || a.name.localeCompare(b.name));
}

export function getAcademyAnalytics(now = new Date()): AcademyAnalytics {
  const snapshot = getAcademyTelemetrySnapshot();
  const source = process.env.AIRA_ACADEMY_TELEMETRY_JSON ? "environment_snapshot" : "not_configured";
  const day = now.toISOString().slice(0, 10);
  const events = snapshot.events;
  const started = events.filter((event) => event.type === "lesson_started").length;
  const completedEvents = events.filter((event) => event.type === "lesson_completed").length;
  const completedLessons = Math.max(completedEvents, snapshot.students.reduce((sum, student) => sum + Math.max(0, student.completedLessons || 0), 0));
  const languages = countBy(snapshot.students.map((student) => student.learningLanguage));
  const levels = countBy(snapshot.students.map((student) => student.level));

  return {
    source,
    generatedAt: snapshot.generatedAt ?? null,
    totalStudents: snapshot.students.length,
    activeToday: snapshot.students.filter((student) => student.lastActiveAt?.slice(0, 10) === day).length,
    completedLessons,
    tutorSessions: events.filter((event) => event.type === "tutor_session").length,
    voiceSessions: events.filter((event) => event.type === "voice_session").length,
    completionRate: started > 0 ? Math.round((completedEvents / started) * 1000) / 10 : null,
    topLanguage: languages[0]?.name ?? null,
    topLevel: levels[0]?.name ?? null,
    languages,
    levels,
  };
}
