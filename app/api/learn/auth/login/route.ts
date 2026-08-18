import { NextResponse } from "next/server";
import { z } from "zod";
import { setStudentSession, signInStudent } from "../../../../../lib/academy/student-auth";

const Input = z.object({ email: z.string().email(), password: z.string().min(8) });

export async function POST(req: Request) {
  const parsed = Input.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json({ error: "INVALID_INPUT" }, { status: 400 });
  const result = await signInStudent(parsed.data.email, parsed.data.password);
  if (!result.ok) return NextResponse.json({ error: result.code }, { status: result.code === "AUTH_NOT_CONFIGURED" ? 503 : 401 });
  setStudentSession(result.accessToken, result.refreshToken, result.expiresIn);
  return NextResponse.json({ ok: true });
}
