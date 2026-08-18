import Link from "next/link";
import { getAcademyAnalytics } from "@/lib/academy/telemetry";

export const dynamic = "force-dynamic";

export default function Analytics(){
  const analytics = getAcademyAnalytics();
  const configured = analytics.source !== "not_configured";
  return <main>
    <div className="page-head"><div><p className="eyebrow">FOUNDER · АНАЛИТИКА</p><h1>Learning Analytics</h1><p className="muted">Метрики обучения из server-side student records и learner events.</p></div><Link className="button" href="/developer">← Кабинет основателя</Link></div>
    <section className="card"><h2>Telemetry status</h2><p className="muted">{configured ? `Источник подключён${analytics.generatedAt ? ` · snapshot ${analytics.generatedAt}` : ""}.` : "Источник persistent telemetry пока не подключён. Расчёты уже работают на server data contract; до появления данных значения остаются нулевыми или «—»."}</p></section>
    <div className="grid" style={{marginTop:16}}>
      <article className="card metric"><span className="eyebrow">COMPLETION RATE</span><div className="value">{analytics.completionRate === null ? "—" : `${analytics.completionRate}%`}</div><span className="muted">lesson_completed / lesson_started</span></article>
      <article className="card metric"><span className="eyebrow">АКТИВНЫЕ СЕГОДНЯ</span><div className="value">{analytics.activeToday}</div><span className="muted">Уникальные student records</span></article>
      <article className="card metric"><span className="eyebrow">TOP LANGUAGE</span><div className="value">{analytics.topLanguage || "—"}</div><span className="muted">По числу учеников</span></article>
      <article className="card metric"><span className="eyebrow">TUTOR SESSIONS</span><div className="value">{analytics.tutorSessions}</div><span className="muted">Server learner events</span></article>
      <article className="card metric"><span className="eyebrow">VOICE SESSIONS</span><div className="value">{analytics.voiceSessions}</div><span className="muted">Server learner events</span></article>
      <article className="card metric"><span className="eyebrow">TOP LEVEL</span><div className="value">{analytics.topLevel || "—"}</div><span className="muted">По student records</span></article>
    </div>
    <div className="two-col" style={{marginTop:20}}>
      <section className="card"><h2>Языки</h2>{analytics.languages.length ? analytics.languages.map(item=><p key={item.name}><strong>{item.name}</strong> · {item.students}</p>) : <p className="muted">Нет данных по языкам.</p>}</section>
      <section className="card"><h2>Уровни</h2>{analytics.levels.length ? analytics.levels.map(item=><p key={item.name}><strong>{item.name}</strong> · {item.students}</p>) : <p className="muted">Нет данных по уровням.</p>}</section>
    </div>
    <div className="controls" style={{marginTop:20}}><Link className="button" href="/api/developer/data/analytics">Открыть Analytics API →</Link><Link className="button" href="/developer/students">Открыть учеников →</Link></div>
  </main>
}
