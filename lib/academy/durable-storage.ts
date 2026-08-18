import type { LearningEvent, StudentRecord } from "./telemetry";

const url = process.env.AIRA_SUPABASE_URL?.replace(/\/$/, "");
const key = process.env.AIRA_SUPABASE_SERVICE_ROLE_KEY;

function configured() { return Boolean(url && key); }
function headers(extra: Record<string,string> = {}) { return { apikey: key!, Authorization: `Bearer ${key}`, "Content-Type": "application/json", ...extra }; }

export function durableStorageConfigured() { return configured(); }

export async function upsertStudent(student: StudentRecord) {
  if (!configured()) return false;
  const res = await fetch(`${url}/rest/v1/academy_students?on_conflict=id`, { method: "POST", headers: headers({ Prefer: "resolution=merge-duplicates,return=minimal" }), body: JSON.stringify(student), cache: "no-store" });
  return res.ok;
}

export async function insertLearningEvent(event: LearningEvent) {
  if (!configured()) return false;
  const res = await fetch(`${url}/rest/v1/academy_events`, { method: "POST", headers: headers({ Prefer: "return=minimal" }), body: JSON.stringify(event), cache: "no-store" });
  return res.ok;
}

export async function readStudent(id: string): Promise<StudentRecord | null> {
  if (!configured()) return null;
  const res = await fetch(`${url}/rest/v1/academy_students?id=eq.${encodeURIComponent(id)}&select=*&limit=1`, { headers: headers(), cache: "no-store" });
  if (!res.ok) return null;
  const rows = await res.json() as StudentRecord[];
  return rows[0] ?? null;
}

export async function readStudents(): Promise<StudentRecord[]> {
  if (!configured()) return [];
  const res = await fetch(`${url}/rest/v1/academy_students?select=*&order=lastActiveAt.desc.nullslast`, { headers: headers(), cache: "no-store" });
  return res.ok ? await res.json() : [];
}

export async function readEvents(): Promise<LearningEvent[]> {
  if (!configured()) return [];
  const res = await fetch(`${url}/rest/v1/academy_events?select=*&order=createdAt.desc`, { headers: headers(), cache: "no-store" });
  return res.ok ? await res.json() : [];
}
