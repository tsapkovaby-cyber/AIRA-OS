"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "../learn.module.css";
import { hydrateLearnerProfileFromAccount } from "../../../lib/learner-profile";

export default function SignIn(){
  const router=useRouter();
  const [mode,setMode]=useState<"login"|"signup">("login");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [busy,setBusy]=useState(false);
  const [message,setMessage]=useState("");

  async function submit(e:FormEvent){
    e.preventDefault(); setBusy(true); setMessage("");
    try{
      const res=await fetch(`/api/learn/auth/${mode}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password})});
      const data=await res.json();
      if(!res.ok){setMessage(data.error==="AUTH_NOT_CONFIGURED"?"Аккаунты учеников ещё не подключены к Supabase Auth.":"Не удалось войти. Проверь email и пароль.");return;}
      if(data.confirmationRequired){setMessage("Аккаунт создан. Подтверди email, затем войди.");setMode("login");return;}
      await hydrateLearnerProfileFromAccount();
      router.push("/learn"); router.refresh();
    }catch{setMessage("Сервис входа временно недоступен.");}finally{setBusy(false);}
  }

  return <div className={styles.authPage}><form className={styles.authCard} onSubmit={submit}><div className={styles.brandMark}>A</div><span className={styles.eyebrow}>AIRA ACADEMY</span><h1>{mode==="login"?"Вход ученика":"Создать аккаунт"}</h1><p>{mode==="login"?"Войди, чтобы продолжить обучение с сохранённого места на любом устройстве.":"Создай единый аккаунт для синхронизации прогресса между устройствами."}</p><label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" required /></label><label>Пароль<input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Минимум 8 символов" minLength={8} required /></label><button className={styles.primaryButton} type="submit" disabled={busy}>{busy?"Подождите…":mode==="login"?"Войти":"Создать аккаунт"}</button>{message&&<p>{message}</p>}<button className={styles.secondaryButton} type="button" onClick={()=>{setMode(mode==="login"?"signup":"login");setMessage("");}}>{mode==="login"?"Нет аккаунта? Зарегистрироваться":"Уже есть аккаунт? Войти"}</button><Link href="/learn">Продолжить без аккаунта →</Link><small>Без аккаунта прогресс остаётся доступен локально. После входа AIRA Academy использует защищённую HTTP-only сессию и облачную синхронизацию.</small></form></div>;
}
