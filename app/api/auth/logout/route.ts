import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("aira_session");
  response.cookies.delete("aira_csrf");
  return response;
}
