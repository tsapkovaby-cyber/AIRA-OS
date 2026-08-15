"use client";

import { FormEvent, useState } from "react";

export default function DeveloperLogin() {
  const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setLoading(true); setError(""); const form=new FormData(event.currentTarget); const response=await fetch("/api/developer/login",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(Object.fromEntries(form))}); setLoading(false); if(response.ok){const next=new URLSearchParams(window.location.search).get("next");window.location.href=next?.startsWith("/developer")?next:"/developer";return;} setError(response.status===503?"Доступ основателя ещё не настроен в окружении.":"Неверный email или пароль."); }
  return <main className="login"><form className="login-card" onSubmit={submit}><p className="eyebrow">AIRA Academy · ДОСТУП ОСНОВАТЕЛЯ</p><h1>Вход в кабинет основателя</h1><p className="muted">Закрытый доступ к управлению AIRA Academy и инструментам разработчика.</p><label className="field"><span>Email</span><input name="email" type="email" autoComplete="username" required autoFocus /></label><label className="field"><span>Пароль</span><input name="password" type="password" autoComplete="current-password" minLength={8} required /></label>{error&&<p role="alert">{error}</p>}<button className="button primary" style={{width:"100%"}} disabled={loading}>{loading?"Входим…":"Войти как основатель"}</button><a href="/academy" className="muted">← Вернуться в Academy</a></form></main>;
}
