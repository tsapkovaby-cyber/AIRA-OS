import { NextResponse } from "next/server";
import { getLiveAcademyTelemetry } from "@/lib/academy/live-telemetry";

export const dynamic = "force-dynamic";

export async function GET() {
  const { analytics } = await getLiveAcademyTelemetry();
  return NextResponse.json(analytics);
}
