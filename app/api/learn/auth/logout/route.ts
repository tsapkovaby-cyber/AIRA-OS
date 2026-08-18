import { NextResponse } from "next/server";
import { clearStudentSession } from "../../../../../lib/academy/student-auth";

export async function POST() {
  clearStudentSession();
  return NextResponse.json({ ok: true });
}
