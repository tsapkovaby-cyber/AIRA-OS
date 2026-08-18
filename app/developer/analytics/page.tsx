import Link from "next/link";
import { getLiveAcademyTelemetry } from "@/lib/academy/live-telemetry";

export const dynamic = "force-dynamic";

const eventLabels: Record<string,string> = {
  lesson_started: "Урок начат",
  lesson_completed: "Урок завершён",
  practice_started: "Практика начата",
  tutor_session: "AIRA Tutor",
  voice_session: "Voice Tutor",
};

export default async function Analytics(){
  const { source, analytics } = await getLiveAcademyTelemetry();
  const configured = source !== "not_configured";
  const sourceLabel = source === "supabase_live" ? "Supabase live storage" : source === "environment_snapshot" ? "server telemetry snapshot" : "не подключён";
  return <main>
    <div className="page-head"><div><p className="eyebrow">FOUNDER · АНАЛИТИКА</p><h1>Learning Analytics</h1><p className="muted">Метрики обучения из реальных student records и learner events.</p></div><Link className="button" href="/developer">← Кабинет основателя</Link></div>
    <section className="card"><h2>Telemetry status</h2><p className="muted">{configured ? `${sourceLabel}${analytics.generatedAt ? ` · обновлено ${analytics.generatedAt}` : ""}.` : "Источник persistent telemetry пока не подключён. До появления данных значения остаются нулевыми или «—»."}</p></section>
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
    <section className="card" style={{marginTop:20}}><h2>Последние учебные события</h2>{analytics.recentEvents.length ? <div className="table-wrap"><table><thead><tr><th>Событие</th><th>Ученик</th><th>Язык</th><th>Уровень</th><th>Время</th></tr></thead><tbody>{analytics.recentEvents.map(event=><tr key={event.id}><td>{eventLabels[event.type] || event.type}</td><td>{event.studentId}</td><td>{event.language || "—"}</td><td>{event.level || "—"}</td><td>{event.createdAt}</td></tr>)}</tbody></table></div> : <p className="muted">Пока нет learner events.</p>}</section>
    <div className="controls" style={{marginTop:20}}><Link className="button" href="/api/developer/data/analytics">Открыть Analytics API →</Link><Link className="button" href="/developer/students">Открыть учеников →</Link></div>
  </main>
}
