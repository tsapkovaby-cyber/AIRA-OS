import { NextResponse } from "next/server";
import { durableStorageConfigured } from "../../../../lib/academy/durable-storage";
import { getStudentIdentity, studentAuthConfigured } from "../../../../lib/academy/student-auth";

export const dynamic = "force-dynamic";

export async function GET() {
  const identity = await getStudentIdentity();
  return NextResponse.json({
    authConfigured: studentAuthConfigured(),
    storageConfigured: durableStorageConfigured(),
    authenticated: Boolean(identity),
    user: identity,
  });
}
