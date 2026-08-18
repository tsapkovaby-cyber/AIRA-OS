import { NextResponse } from "next/server";
import { getAcademyAnalytics } from "@/lib/academy/telemetry";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json(getAcademyAnalytics());
}
