"use client";

import { FormEvent, useState } from "react";

export default function Login() {
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(Object.fromEntries(form)),
    });
    if (response.ok) location.href = "/dashboard";
    else setError("Credentials were not accepted. Reference: AUTH-401");
  }

  return (
    <main className="login">
      <form className="login-card" onSubmit={submit}>
        <p className="eyebrow">AIRA OS · SECURE ACCESS</p>
        <h1>Founder Control Center</h1>
        <p className="muted">Sign in with the Founder credentials configured in the deployment environment.</p>
        <label className="field"><span>Email</span><input name="email" type="email" required autoFocus /></label>
        <label className="field"><span>Password</span><input name="password" type="password" required /></label>
        {error && <p role="alert" style={{ color: "var(--red)" }}>{error}</p>}
        <button className="button primary" style={{ width: "100%" }}>Sign in securely</button>
      </form>
    </main>
  );
}
