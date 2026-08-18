import { NextResponse } from "next/server";
import { z } from "zod";
import { randomUUID } from "crypto";
import { insertLearningEvent } from "../../../../lib/academy/durable-storage";

const EventInput = z.object({
  studentId: z.string().min(3),
  type: z.enum(["lesson_started","lesson_completed","practice_started","tutor_session","voice_session"]),
  language: z.string().optional(),
  level: z.string().optional(),
  lessonId: z.string().optional(),
});

export async function POST(req: Request) {
  const parsed = EventInput.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json({ error: "INVALID_EVENT" }, { status: 400 });
  const stored = await insertLearningEvent({ id: randomUUID(), ...parsed.data, createdAt: new Date().toISOString() });
  return NextResponse.json({ stored }, { status: stored ? 201 : 202 });
}
