import { NextResponse } from "next/server";
import { getAcademyTelemetrySnapshot } from "@/lib/academy/telemetry";

export const dynamic = "force-dynamic";

export async function GET() {
  const snapshot = getAcademyTelemetrySnapshot();
  return NextResponse.json({
    source: process.env.AIRA_ACADEMY_TELEMETRY_JSON ? "environment_snapshot" : "not_configured",
    generatedAt: snapshot.generatedAt ?? null,
    students: snapshot.students,
  });
}
