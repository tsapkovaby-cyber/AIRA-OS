import { NextResponse } from "next/server";
import { durableStorageConfigured, readStudents } from "@/lib/academy/durable-storage";
import { getAcademyTelemetrySnapshot } from "@/lib/academy/telemetry";

export const dynamic = "force-dynamic";

export async function GET() {
  if (durableStorageConfigured()) {
    const students = await readStudents();
    return NextResponse.json({
      source: "supabase_live",
      generatedAt: new Date().toISOString(),
      students,
    });
  }

  const snapshot = getAcademyTelemetrySnapshot();
  return NextResponse.json({
    source: process.env.AIRA_ACADEMY_TELEMETRY_JSON ? "environment_snapshot" : "not_configured",
    generatedAt: snapshot.generatedAt ?? null,
    students: snapshot.students,
  });
}
