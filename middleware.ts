import { NextRequest, NextResponse } from "next/server";

async function ownerSessionValue(email: string, password: string) {
  const input = new TextEncoder().encode(`aira-academy-owner:${email}:${password}`);
  const digest = await crypto.subtle.digest("SHA-256", input);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function protectDeveloper(request: NextRequest) {
  const expectedEmail = process.env.AIRA_PREVIEW_OWNER_EMAIL;
  const expectedPassword = process.env.AIRA_PREVIEW_OWNER_PASSWORD;
  if (!expectedEmail || !expectedPassword) {
    return new NextResponse("AIRA Academy Owner / Developer access is not configured.", { status: 503 });
  }

  const expectedSession = await ownerSessionValue(expectedEmail, expectedPassword);
  const actualSession = request.cookies.get("aira_owner_session")?.value;
  if (actualSession !== expectedSession) {
    if (request.nextUrl.pathname.startsWith("/api/developer/data")) {
      return NextResponse.json({ error: "owner_auth_required" }, { status: 401 });
    }
    const login = new URL("/developer-login", request.url);
    login.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

function protectDashboard(request: NextRequest) {
  const expected = process.env.AIRA_DASHBOARD_SESSION_TOKEN;
  const actual = request.cookies.get("aira_session")?.value;
  if (!expected || !actual || actual !== expected) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}

export async function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/developer") || request.nextUrl.pathname.startsWith("/api/developer/data")) return protectDeveloper(request);
  if (request.nextUrl.pathname.startsWith("/dashboard")) return protectDashboard(request);
  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*", "/developer/:path*", "/api/developer/data/:path*"] };
