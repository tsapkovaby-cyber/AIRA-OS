"use client";

import { FormEvent, useState } from "react";
import { useSearchParams } from "next/navigation";

export default function DeveloperLogin() {
  const searchParams = useSearchParams();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/developer/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(Object.fromEntries(form)),
    });
    setLoading(false);
    if (response.ok) {
      const next = searchParams.get("next");
      location.href = next?.startsWith("/developer") ? next : "/developer";
      return;
    }
    setError(response.status === 503 ? "Owner access is not configured." : "Email or password is incorrect.");
  }

  return (
    <main className="login">
      <form className="login-card" onSubmit={submit}>
        <p className="eyebrow">AIRA Academy · OWNER ACCESS</p>
        <h1>Developer sign in</h1>
        <p className="muted">Private access for the AIRA Academy owner and developer account.</p>
        <label className="field"><span>Email</span><input name="email" type="email" autoComplete="username" required autoFocus /></label>
        <label className="field"><span>Password</span><input name="password" type="password" autoComplete="current-password" minLength={8} required /></label>
        {error && <p role="alert">{error}</p>}
        <button className="button primary" style={{ width: "100%" }} disabled={loading}>{loading ? "Signing in…" : "Sign in as Owner"}</button>
        <a href="/academy" className="muted">← Back to Academy</a>
      </form>
    </main>
  );
}
