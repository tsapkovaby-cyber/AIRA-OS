import { NextRequest, NextResponse } from "next/server";
export function middleware(request: NextRequest) {
  if (!request.cookies.get("aira_session")?.value) {
    const login = new URL("/login", request.url); login.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(login);
  }
  return NextResponse.next();
}
export const config = { matcher: ["/dashboard/:path*"] };
