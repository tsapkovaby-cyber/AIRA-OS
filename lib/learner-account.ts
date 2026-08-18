export type LearnerAccountStatus = {
  authConfigured: boolean;
  storageConfigured: boolean;
  authenticated: boolean;
  user: { id: string; email?: string } | null;
};

export async function loadLearnerAccountStatus(): Promise<LearnerAccountStatus> {
  try {
    const res = await fetch("/api/learn/account", { cache: "no-store" });
    if (!res.ok) throw new Error("ACCOUNT_STATUS_FAILED");
    return await res.json();
  } catch {
    return { authConfigured: false, storageConfigured: false, authenticated: false, user: null };
  }
}

export async function signOutLearner() {
  const res = await fetch("/api/learn/auth/logout", { method: "POST" });
  return res.ok;
}
