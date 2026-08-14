"use client";

import { useState } from "react";

function csrfToken(): string {
  const entry = document.cookie.split("; ").find((item) => item.startsWith("aira_csrf="));
  return entry ? decodeURIComponent(entry.split("=").slice(1).join("=")) : "";
}

export function ConfirmAction({ label, danger = false }: { label: string; danger?: boolean }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");

  async function confirm() {
    const response = await fetch("/api/actions", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-csrf-token": csrfToken(),
      },
      body: JSON.stringify({ action: label, objectVersion: 1, reason: "Founder confirmed via dashboard" }),
    });
    setOpen(false);
    const payload = await response.json().catch(() => ({}));
    setMessage(response.ok ? `Action accepted and audited · ${payload?.data?.auditId ?? "audit recorded"}` : "Action was rejected by server policy.");
  }

  return (
    <>
      <button className={`button ${danger ? "danger" : ""}`} onClick={() => setOpen(true)}>{label}</button>
      {open && (
        <div className="dialog-backdrop" role="presentation">
          <section className="dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
            <p className="eyebrow">Explicit confirmation required</p>
            <h2 id="confirm-title">Confirm {label}?</h2>
            <p>This action is submitted to the server and must pass the Founder session and CSRF checks.</p>
            <div className="dialog-actions">
              <button className="button" onClick={() => setOpen(false)} autoFocus>Cancel</button>
              <button className={`button ${danger ? "danger" : "primary"}`} onClick={confirm}>Confirm action</button>
            </div>
          </section>
        </div>
      )}
      {message && <div role="status" className="toast">{message}</div>}
    </>
  );
}
