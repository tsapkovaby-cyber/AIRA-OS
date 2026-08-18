import Link from "next/link";
import { getLiveAcademyTelemetry } from "@/lib/academy/live-telemetry";

export const dynamic = "force-dynamic";

export default async function FounderStudents(){
  const { source, snapshot, analytics } = await getLiveAcademyTelemetry();
  const configured = source !== "not_configured";
  const sourceLabel = source === "supabase_live" ? "Supabase live storage" : source === "environment_snapshot" ? "server telemetry snapshot" : "не подключён";
  return <main>
    <div className="page-head"><div><p className="eyebrow">FOUNDER · УЧЕНИКИ</p><h1>Ученики и доступы</h1><p className="muted">Реальные student records, языки, уровни, прогресс и статусы доступа.</p></div><Link className="button" href="/developer">← Кабинет основателя</Link></div>
    <section className="card"><h2>Источник данных</h2><p className="muted">{configured ? `${sourceLabel}${analytics.generatedAt ? ` · обновлено ${analytics.generatedAt}` : ""}.` : "Постоянное student storage ещё не подключено. Кабинет показывает честные нули до подключения источника."}</p></section>
    <div className="grid" style={{marginTop:16}}>
      <article className="card metric"><span className="eyebrow">ВСЕГО УЧЕНИКОВ</span><div className="value">{analytics.totalStudents}</div><span className="muted">Server student records</span></article>
      <article className="card metric"><span className="eyebrow">АКТИВНЫЕ СЕГОДНЯ</span><div className="value">{analytics.activeToday}</div><span className="muted">По lastActiveAt</span></article>
      <article className="card metric"><span className="eyebrow">ЗАВЕРШЁННЫЕ УРОКИ</span><div className="value">{analytics.completedLessons}</div><span className="muted">Progress events + student totals</span></article>
      <article className="card metric"><span className="eyebrow">VOICE СЕССИИ</span><div className="value">{analytics.voiceSessions}</div><span className="muted">Server telemetry</span></article>
    </div>
    <section className="table-wrap" style={{marginTop:20}}><table><thead><tr><th>Ученик</th><th>Язык</th><th>Уровень</th><th>Уроки</th><th>Streak</th><th>Статус</th><th>Последняя активность</th></tr></thead><tbody>{snapshot.students.length ? snapshot.students.map(student=><tr key={student.id}><td>{student.displayName || student.email || student.id}</td><td>{student.learningLanguage || "—"}</td><td>{student.level || "—"}</td><td>{student.completedLessons || 0}</td><td>{student.streak || 0}</td><td>{student.accessStatus || "active"}</td><td>{student.lastActiveAt || "—"}</td></tr>) : <tr><td colSpan={7} className="empty">Нет student records. После подключения persistent storage таблица заполнится автоматически.</td></tr>}</tbody></table></section>
    <div className="controls" style={{marginTop:20}}><Link className="button" href="/api/developer/data/students">Открыть Students API →</Link><Link className="button" href="/developer/analytics">Перейти к аналитике →</Link></div>
  </main>
}
