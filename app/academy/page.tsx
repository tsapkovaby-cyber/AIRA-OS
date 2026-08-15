import Link from 'next/link';

const languages = [
  ['English','EN'],['Русский','RU'],['Español','ES'],['Italiano','IT'],['Türkçe','TR'],
  ['Қазақша','KK'],['Français','FR'],['Deutsch','DE'],['한국어','KO'],['简体中文','ZH']
];

export default function AcademyPreview(){
  return <main className="student-app">
    <aside className="student-sidebar">
      <Link href="/academy" className="student-brand">AIRA<span>Academy</span></Link>
      <nav className="student-nav">
        <Link className="active" href="/academy">⌂ <span>Home</span></Link>
        <Link href="/learn">◇ <span>Learn</span></Link>
        <Link href="/learn/catalog">◎ <span>Languages</span></Link>
        <Link href="/learn/tutor">✦ <span>AIRA Tutor</span></Link>
        <Link href="/learn/progress">↗ <span>Progress</span></Link>
      </nav>
      <div className="student-sidebar-bottom"><p className="student-mini-label">YOUR ACADEMY</p><Link href="/developer">Owner workspace</Link></div>
    </aside>

    <section className="student-content">
      <header className="student-topbar"><div><p className="student-mini-label">AIRA ACADEMY</p><strong>Language learning, made personal.</strong></div><div className="student-profile"><span>7 day streak</span><b>A</b></div></header>

      <div className="student-page">
        <section className="student-welcome">
          <div><p className="student-mini-label">WELCOME BACK</p><h1>Ready for your next lesson?</h1><p>AIRA adapts lessons, explanations and practice to the language you already understand.</p></div>
          <div className="student-streak"><span>🔥</span><strong>7</strong><small>day streak</small></div>
        </section>

        <section className="continue-card">
          <div className="course-badge">EN</div><div className="continue-copy"><p className="student-mini-label">CONTINUE LEARNING</p><h2>English · Beginner path</h2><p>Everyday conversation · Lesson 4 of 12</p><div className="progress-track"><span style={{width:'32%'}} /></div><small>32% complete</small></div><Link href="/learn/courses" className="student-primary">Continue lesson →</Link>
        </section>

        <div className="student-section-head"><div><p className="student-mini-label">LEARN WITH AIRA</p><h2>Your learning tools</h2></div></div>
        <section className="learning-tools">
          <article className="learning-tool featured"><span className="tool-icon">✦</span><h3>AIRA Tutor</h3><p>Ask questions and get explanations in your own language.</p><Link href="/learn/tutor">Start a conversation →</Link></article>
          <article className="learning-tool"><span className="tool-icon">◉</span><h3>Voice Tutor</h3><p>Practice real conversations, pronunciation and listening.</p><Link href="/learn/tutor">Open practice modes →</Link></article>
          <article className="learning-tool"><span className="tool-icon">▶</span><h3>Video lessons</h3><p>Short guided lessons with AIRA, built around your current level.</p><Link href="/learn/courses">Open learning path →</Link></article>
        </section>

        <div className="student-section-head"><div><p className="student-mini-label">LANGUAGE CATALOG</p><h2>Choose what you want to learn</h2></div><Link href="/learn/catalog">View all paths →</Link></div>
        <section className="student-language-grid">{languages.map(([name,code])=><Link className="student-language" href="/learn/catalog" key={code}><span>{code}</span><div><strong>{name}</strong><small>Personal learning path</small></div><b>→</b></Link>)}</section>

        <section className="student-progress-card"><div><p className="student-mini-label">YOUR PROGRESS</p><h2>Small steps become fluency.</h2><p>Lessons, tutor practice, voice sessions and video activity will come together in one learning history.</p><Link href="/learn/progress">View detailed progress →</Link></div><div className="progress-stats"><div><strong>4</strong><span>lessons</span></div><div><strong>32%</strong><span>current path</span></div><div><strong>7</strong><span>day streak</span></div></div></section>
      </div>
    </section>
  </main>
}
