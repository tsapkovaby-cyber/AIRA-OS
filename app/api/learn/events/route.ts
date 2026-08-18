import { NextResponse } from "next/server";
import { z } from "zod";
import { randomUUID } from "crypto";
import { insertLearningEvent } from "../../../../lib/academy/durable-storage";
import { getStudentIdentity } from "../../../../lib/academy/student-auth";

const EventInput = z.object({
  studentId: z.string().min(3).optional(),
  type: z.enum(["lesson_started","lesson_completed","practice_started","tutor_session","voice_session"]),
  language: z.string().optional(),
  level: z.string().optional(),
  lessonId: z.string().optional(),
});

export async function POST(req: Request) {
  const parsed = EventInput.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json({ error: "INVALID_EVENT" }, { status: 400 });
  const identity = await getStudentIdentity();
  const studentId = identity?.id ?? parsed.data.studentId;
  if (!studentId) return NextResponse.json({ error: "STUDENT_ID_REQUIRED" }, { status: 400 });
  const stored = await insertLearningEvent({ id: randomUUID(), ...parsed.data, studentId, createdAt: new Date().toISOString() });
  return NextResponse.json({ stored, accountLinked: Boolean(identity), studentId }, { status: stored ? 201 : 202 });
}
