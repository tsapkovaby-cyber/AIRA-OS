"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export default function SiteOps(){
  const [health,setHealth]=useState<"checking"|"online"|"error">("checking");
  const [checkedAt,setCheckedAt]=useState("");
  async function check(){setHealth("checking");try{const r=await fetch("/api/health",{cache:"no-store"});setHealth(r.ok?"online":"error");}catch{setHealth("error");}setCheckedAt(new Date().toLocaleTimeString());}
  useEffect(()=>{check();},[]);
  return <main><div className="page-head"><div><p className="eyebrow">FOUNDER · SITE OPS</p><h1>Сайт и деплои</h1><p className="muted">Операционный экран production, health, маршрутов и ручной проверки Academy.</p></div><Link className="button" href="/developer">← Кабинет основателя</Link></div>
  <div className="grid"><article className="card metric"><span className="eyebrow">PRODUCTION</span><div className="value">Online</div><span className="trend">aira-academy-eta.vercel.app</span></article><article className="card metric"><span className="eyebrow">API HEALTH</span><div className="value">{health==="checking"?"…":health==="online"?"OK":"Error"}</div><span className="muted">{checkedAt?`Проверено ${checkedAt}`:"Проверяется"}</span></article><article className="card metric"><span className="eyebrow">STUDENT APP</span><div className="value">/learn</div><span className="muted">Учебный интерфейс</span></article><article className="card metric"><span className="eyebrow">OWNER</span><div className="value">Protected</div><span className="muted">/developer</span></article></div>
  <section className="card" style={{marginTop:20}}><div className="section-head"><h2>Быстрые проверки</h2><button className="button primary" onClick={check}>Проверить health</button></div><div className="controls"><Link className="button" href="/academy">Открыть Academy</Link><Link className="button" href="/learn">Проверить /learn</Link><Link className="button" href="/learn/catalog">Каталог</Link><Link className="button" href="/learn/lesson">Урок</Link><Link className="button" href="/api/health">Health JSON</Link></div></section>
  <section className="card" style={{marginTop:20}}><h2>Deployment telemetry</h2><p className="muted">Веб-интерфейс уже умеет проверять runtime health. История Vercel production/preview и build errors будет подключена через серверный founder API, чтобы токены Vercel никогда не попадали в браузер.</p><div className="attention"><span className="dot"/><div><strong>Production routing</strong><span className="muted">Работает через основной домен Academy.</span></div></div><div className="attention"><span className="dot"/><div><strong>Health endpoint</strong><span className="muted">Проверяется прямо из этого экрана.</span></div></div><div className="attention"><span className="dot red"/><div><strong>Vercel history API</strong><span className="muted">Server-side connector ещё не подключён к UI.</span></div></div></section></main>;
}
