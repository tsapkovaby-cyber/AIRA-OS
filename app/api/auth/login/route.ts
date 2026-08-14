import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import { z } from "zod";

const Login = z.object({ email: z.string().email(), password: z.string().min(8) });

export async function POST(req: Request) {
  const parsed = Login.safeParse(await req.json());
  const expectedEmail = process.env.AIRA_DASHBOARD_EMAIL;
  const expectedPassword = process.env.AIRA_DASHBOARD_PASSWORD;
  const sessionToken = process.env.AIRA_DASHBOARD_SESSION_TOKEN;

  if (!expectedEmail || !expectedPassword || !sessionToken) {
    return NextResponse.json(
      { error: { code: "AUTH_NOT_CONFIGURED", referenceId: "AUTH-503" } },
      { status: 503 },
    );
  }
  if (!parsed.success || parsed.data.email !== expectedEmail || parsed.data.password !== expectedPassword) {
    return NextResponse.json(
      { error: { code: "UNAUTHORIZED", referenceId: "AUTH-401" } },
      { status: 401 },
    );
  }

  const response = NextResponse.json({ user: { id: "founder", role: "OWNER" } });
  response.cookies.set("aira_session", sessionToken, {
    httpOnly: true,
    sameSite: "strict",
    secure: process.env.NODE_ENV === "production",
    maxAge: 3600,
    path: "/",
  });
  response.cookies.set("aira_csrf", randomUUID(), {
    httpOnly: false,
    sameSite: "strict",
    secure: process.env.NODE_ENV === "production",
    maxAge: 3600,
    path: "/",
  });
  return response;
}
