import { createHash, timingSafeEqual } from "crypto";
import { NextResponse } from "next/server";
import { z } from "zod";

const Login = z.object({ email: z.string().email(), password: z.string().min(8) });

function safeEqual(left: string, right: string) {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);
  return leftBuffer.length === rightBuffer.length && timingSafeEqual(leftBuffer, rightBuffer);
}

function ownerSessionValue(email: string, password: string) {
  return createHash("sha256").update(`aira-academy-owner:${email}:${password}`).digest("hex");
}

export async function POST(request: Request) {
  const parsed = Login.safeParse(await request.json());
  const expectedEmail = process.env.AIRA_PREVIEW_OWNER_EMAIL;
  const expectedPassword = process.env.AIRA_PREVIEW_OWNER_PASSWORD;

  if (!expectedEmail || !expectedPassword) {
    return NextResponse.json({ error: { code: "OWNER_AUTH_NOT_CONFIGURED" } }, { status: 503 });
  }
  if (
    !parsed.success ||
    !safeEqual(parsed.data.email, expectedEmail) ||
    !safeEqual(parsed.data.password, expectedPassword)
  ) {
    return NextResponse.json({ error: { code: "UNAUTHORIZED" } }, { status: 401 });
  }

  const response = NextResponse.json({ user: { id: "founder", role: "OWNER" } });
  response.cookies.set("aira_owner_session", ownerSessionValue(expectedEmail, expectedPassword), {
    httpOnly: true,
    sameSite: "strict",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 8,
    path: "/",
  });
  return response;
}
