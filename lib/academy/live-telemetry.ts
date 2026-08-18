import { durableStorageConfigured, readEvents, readStudents } from "./durable-storage";
import {
  buildAcademyAnalytics,
  getAcademyTelemetrySnapshot,
  type AcademyAnalytics,
  type AcademyTelemetrySnapshot,
  type AcademyTelemetrySource,
} from "./telemetry";

export async function getLiveAcademyTelemetry(): Promise<{
  source: AcademyTelemetrySource;
  snapshot: AcademyTelemetrySnapshot;
  analytics: AcademyAnalytics;
}> {
  if (durableStorageConfigured()) {
    const [students, events] = await Promise.all([readStudents(), readEvents()]);
    const snapshot: AcademyTelemetrySnapshot = {
      generatedAt: new Date().toISOString(),
      students,
      events,
    };
    return {
      source: "supabase_live",
      snapshot,
      analytics: buildAcademyAnalytics(snapshot, "supabase_live"),
    };
  }

  const snapshot = getAcademyTelemetrySnapshot();
  const source: AcademyTelemetrySource = process.env.AIRA_ACADEMY_TELEMETRY_JSON
    ? "environment_snapshot"
    : "not_configured";

  return {
    source,
    snapshot,
    analytics: buildAcademyAnalytics(snapshot, source),
  };
}
