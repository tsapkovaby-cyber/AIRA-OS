import { NextRequest, NextResponse } from "next/server";

function unauthorizedDeveloper() {
  return new NextResponse("AIRA Academy Owner / Developer access required.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="AIRA Academy Developer Preview", charset="UTF-8"' },
  });
}

function protectDeveloper(request: NextRequest) {
  const expectedEmail = process.env.AIRA_PREVIEW_OWNER_EMAIL;
  const expectedPassword = process.env.AIRA_PREVIEW_OWNER_PASSWORD;
  if (!expectedEmail || !expectedPassword) return unauthorizedDeveloper();

  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Basic ")) return unauthorizedDeveloper();

  try {
    const decoded = atob(authorization.slice(6));
    const separator = decoded.indexOf(":");
    if (separator < 0) return unauthorizedDeveloper();
    const email = decoded.slice(0, separator);
    const password = decoded.slice(separator + 1);
    if (email !== expectedEmail || password !== expectedPassword) return unauthorizedDeveloper();
    return NextResponse.next();
  } catch {
    return unauthorizedDeveloper();
  }
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

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith("/developer")) return protectDeveloper(request);
  if (request.nextUrl.pathname.startsWith("/dashboard")) return protectDashboard(request);
  return NextResponse.next();
}

export const config = { matcher: ["/dashboard/:path*", "/developer/:path*"] };
