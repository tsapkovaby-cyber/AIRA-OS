import { NextResponse } from "next/server";
import { z } from "zod";
import { readStudent, upsertStudent } from "../../../../lib/academy/durable-storage";
import { getStudentIdentity } from "../../../../lib/academy/student-auth";

const ProfileInput = z.object({
  id: z.string().min(3).optional(),
  email: z.string().email().optional(),
  displayName: z.string().optional(),
  learningLanguage: z.string().min(1),
  level: z.string().min(1),
  streak: z.number().int().min(0),
  completedLessons: z.number().int().min(0),
  lastActiveAt: z.string().nullable().optional(),
  accessStatus: z.enum(["active","trial","paused","blocked"]).optional(),
});

export async function GET() {
  const identity = await getStudentIdentity();
  if (!identity) return NextResponse.json({ authenticated: false, profile: null }, { status: 401 });
  const profile = await readStudent(identity.id);
  return NextResponse.json({ authenticated: true, user: identity, profile });
}

export async function POST(req: Request) {
  const parsed = ProfileInput.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json({ error: "INVALID_PROFILE" }, { status: 400 });
  const identity = await getStudentIdentity();
  const id = identity?.id ?? parsed.data.id;
  if (!id) return NextResponse.json({ error: "STUDENT_ID_REQUIRED" }, { status: 400 });
  const stored = await upsertStudent({
    ...parsed.data,
    id,
    email: identity?.email ?? parsed.data.email,
    lastActiveAt: parsed.data.lastActiveAt ?? undefined,
  });
  return NextResponse.json({ stored, accountLinked: Boolean(identity), studentId: id }, { status: stored ? 200 : 202 });
}
