import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const response = NextResponse.redirect(new URL("/academy", request.url), 303);
  response.cookies.set("aira_owner_session", "", {
    httpOnly: true,
    sameSite: "strict",
    secure: process.env.NODE_ENV === "production",
    expires: new Date(0),
    path: "/",
  });
  return response;
}
