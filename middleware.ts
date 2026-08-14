import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const expected = process.env.AIRA_DASHBOARD_SESSION_TOKEN;
  const actual = request.cookies.get("aira_session")?.value;
  if (!expected || !actual || actual !== expected) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*"] };
