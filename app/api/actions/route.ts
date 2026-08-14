import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

const Action = z.object({
  action: z.enum([
    "Pause AIRA",
    "Resume AIRA",
    "Pause All Agents",
    "Resume Agents",
    "Pause Publishing",
    "Resume Publishing",
    "Emergency Stop",
  ]),
  objectVersion: z.number().int().positive(),
  reason: z.string().min(3),
});

export async function POST(req: NextRequest) {
  const expectedSession = process.env.AIRA_DASHBOARD_SESSION_TOKEN;
  const session = req.cookies.get("aira_session")?.value;
  const csrfCookie = req.cookies.get("aira_csrf")?.value;
  const csrfHeader = req.headers.get("x-csrf-token");

  if (!expectedSession || session !== expectedSession || !csrfCookie || csrfHeader !== csrfCookie) {
    return NextResponse.json(
      { error: { code: "FORBIDDEN", message: "Owner session and CSRF proof required", referenceId: "ACT-403" } },
      { status: 403 },
    );
  }

  const value = Action.safeParse(await req.json());
  if (!value.success) {
    return NextResponse.json(
      { error: { code: "INVALID_ACTION", message: "Action could not be validated", referenceId: "ACT-422" } },
      { status: 422 },
    );
  }

  return NextResponse.json({
    data: {
      status: "ACCEPTED",
      auditId: `AUD-${crypto.randomUUID()}`,
      event: value.data.action === "Emergency Stop" ? "EmergencyStopActivated" : "ConfigurationChanged",
    },
  });
}
