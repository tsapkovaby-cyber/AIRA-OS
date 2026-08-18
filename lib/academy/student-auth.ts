import { cookies } from "next/headers";

const url = process.env.AIRA_SUPABASE_URL?.replace(/\/$/, "");
const anonKey = process.env.AIRA_SUPABASE_ANON_KEY;
const ACCESS_COOKIE = "aira_student_access";
const REFRESH_COOKIE = "aira_student_refresh";

export type StudentIdentity = { id: string; email?: string };

export function studentAuthConfigured() { return Boolean(url && anonKey); }

export async function signInStudent(email: string, password: string) {
  if (!studentAuthConfigured()) return { ok: false as const, code: "AUTH_NOT_CONFIGURED" };
  const res = await fetch(`${url}/auth/v1/token?grant_type=password`, {
    method: "POST",
    headers: { apikey: anonKey!, "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    cache: "no-store",
  });
  if (!res.ok) return { ok: false as const, code: "INVALID_CREDENTIALS" };
  const data = await res.json();
  return { ok: true as const, accessToken: data.access_token as string, refreshToken: data.refresh_token as string, expiresIn: data.expires_in as number };
}

export async function signUpStudent(email: string, password: string) {
  if (!studentAuthConfigured()) return { ok: false as const, code: "AUTH_NOT_CONFIGURED" };
  const res = await fetch(`${url}/auth/v1/signup`, {
    method: "POST",
    headers: { apikey: anonKey!, "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
    cache: "no-store",
  });
  if (!res.ok) return { ok: false as const, code: "SIGNUP_FAILED" };
  const data = await res.json();
  if (!data.access_token) return { ok: true as const, confirmationRequired: true as const };
  return { ok: true as const, confirmationRequired: false as const, accessToken: data.access_token as string, refreshToken: data.refresh_token as string, expiresIn: data.expires_in as number };
}

export function setStudentSession(accessToken: string, refreshToken: string, expiresIn = 3600) {
  const jar = cookies();
  const common = { httpOnly: true, sameSite: "lax" as const, secure: process.env.NODE_ENV === "production", path: "/" };
  jar.set(ACCESS_COOKIE, accessToken, { ...common, maxAge: expiresIn });
  jar.set(REFRESH_COOKIE, refreshToken, { ...common, maxAge: 60 * 60 * 24 * 30 });
}

export function clearStudentSession() {
  const jar = cookies();
  jar.set(ACCESS_COOKIE, "", { path: "/", maxAge: 0 });
  jar.set(REFRESH_COOKIE, "", { path: "/", maxAge: 0 });
}

export async function getStudentIdentity(): Promise<StudentIdentity | null> {
  if (!studentAuthConfigured()) return null;
  const token = cookies().get(ACCESS_COOKIE)?.value;
  if (!token) return null;
  const res = await fetch(`${url}/auth/v1/user`, { headers: { apikey: anonKey!, Authorization: `Bearer ${token}` }, cache: "no-store" });
  if (!res.ok) return null;
  const user = await res.json();
  return { id: user.id, email: user.email };
}
