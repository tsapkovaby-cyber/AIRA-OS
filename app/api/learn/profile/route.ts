import { NextResponse } from "next/server";
import { z } from "zod";
import { upsertStudent } from "../../../../lib/academy/durable-storage";

const ProfileInput = z.object({
  id: z.string().min(3),
  email: z.string().email().optional(),
  displayName: z.string().optional(),
  learningLanguage: z.string().min(1),
  level: z.string().min(1),
  streak: z.number().int().min(0),
  completedLessons: z.number().int().min(0),
  lastActiveAt: z.string().nullable().optional(),
  accessStatus: z.enum(["active","trial","paused","blocked"]).optional(),
});

export async function POST(req: Request) {
  const parsed = ProfileInput.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json({ error: "INVALID_PROFILE" }, { status: 400 });
  const stored = await upsertStudent({ ...parsed.data, lastActiveAt: parsed.data.lastActiveAt ?? undefined });
  return NextResponse.json({ stored }, { status: stored ? 200 : 202 });
}
