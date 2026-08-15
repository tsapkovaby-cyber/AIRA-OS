import Link from "next/link";

const modules = [
  {title:"Students",status:"No data yet",desc:"Accounts, languages, levels, progress, streaks and access status.",href:"/developer#students"},
  {title:"Learning analytics",status:"Waiting for cloud progress",desc:"Completion, drop-off, language and course performance.",href:"/developer#analytics"},
  {title:"Content Studio",status:"Ready for wiring",desc:"Courses, lessons, exercises, quizzes, video and publication workflow.",href:"/developer#content"},
  {title:"AIRA Tutor & Voice",status:"Partial",desc:"Tutor behavior, lesson context, voice practice and quality controls.",href:"/developer#aira"},
  {title:"Site & deployments",status:"Connected",desc:"Production health, previews, releases and technical checks.",href:"/developer#site"},
  {title:"Billing",status:"Not connected",desc:"Plans, subscriptions, payments and revenue when commerce is enabled.",href:"/developer#billing"},
  {title:"Security & audit",status:"Foundation active",desc:"Owner access, administrative events and future audit history.",href:"/developer#security"},
  {title:"Academy settings",status:"Ready",desc:"Languages, features, limits and global learning configuration.",href:"/developer#settings"},
];

const quickActions = [
  ["Open Academy","/academy"],
  ["Student experience","/learn"],
  ["Content catalog","/learn/catalog"],
  ["Test AIRA Tutor","/learn/tutor"],
  ["Check progress UI","/learn/progress"],
];

export default function FounderConsole(){
  return <main>
    <div className="page-head">
      <div><p className="eyebrow">AIRA OS · FOUNDER CONSOLE</p><h1>Command Center</h1><p className="muted">One workspace for Academy operations, learning quality, content, AI systems and platform health.</p></div>
      <div><span className="health">● OWNER MODE</span><form action="/api/developer/logout" method="post" style={{marginTop:12}}><button className="button" type="submit">Sign out</button></form></div>
    </div>

    <section className="brief"><div><span className="eyebrow">LIVE OPERATIONS</span><h2>Founder control stays separate from student subscriptions.</h2><span>Only real connected data is shown. Empty services remain marked as No data yet or Not connected until their backend source is available.</span></div><Link className="button" href="/academy">Open live Academy →</Link></section>

    <div className="grid">
      <article className="card metric"><span className="eyebrow">STUDENTS</span><div className="value">0</div><span className="muted">Cloud student storage not connected yet</span></article>
      <article className="card metric"><span className="eyebrow">COMPLETED LESSONS</span><div className="value">0</div><span className="muted">Waiting for server-side progress events</span></article>
      <article className="card metric"><span className="eyebrow">LANGUAGES</span><div className="value">10</div><span className="trend">Academy catalog active</span></article>
      <article className="card metric"><span className="eyebrow">PLATFORM</span><div className="value">Online</div><span className="trend">Production Academy available</span></article>
    </div>

    <div className="section-head"><h2>Quick actions</h2><span className="muted">Founder shortcuts</span></div>
    <div className="controls">{quickActions.map(([label,href])=><Link key={href} href={href} className="button">{label}</Link>)}</div>

    <div className="section-head"><h2>Operations</h2><span className="muted">AIRA Academy control surface</span></div>
    <div className="grid">{modules.map(item=><article className="card" key={item.title} id={item.href.split('#')[1]}><span className="pill">{item.status}</span><h2>{item.title}</h2><p className="muted">{item.desc}</p><a href={item.href}>Open workspace →</a></article>)}</div>

    <div className="two-col" style={{marginTop:28}}>
      <section className="card"><span className="eyebrow">SYSTEM STATUS</span><h2>Academy services</h2><div className="attention"><span className="dot"/><div><strong>Student cloud storage</strong><span className="muted">Not connected — Sprint 049 integration boundary prepared.</span></div></div><div className="attention"><span className="dot"/><div><strong>Learning analytics</strong><span className="muted">Waiting for server-side learner events.</span></div></div><div className="attention"><span className="dot red"/><div><strong>Billing</strong><span className="muted">Not configured. No paid access is active.</span></div></div><div className="attention"><span className="dot"/><div><strong>AIRA Academy production</strong><span className="muted">Available through the live Academy deployment.</span></div></div></section>
      <section className="card"><span className="eyebrow">FOUNDER ROADMAP</span><h2>Next operational connections</h2><p><strong>1.</strong> Student identity + database</p><p><strong>2.</strong> Real learner event analytics</p><p><strong>3.</strong> Content management actions</p><p><strong>4.</strong> Tutor/Voice quality controls</p><p><strong>5.</strong> Billing and subscription telemetry</p><p><strong>6.</strong> Security/audit event history</p></section>
    </div>
  </main>
}
