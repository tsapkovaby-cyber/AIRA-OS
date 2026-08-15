import Link from 'next/link';

const languages = [
  ['English','EN','🇺🇸'],['Русский','RU','🇷🇺'],['Español','ES','🇪🇸'],['Italiano','IT','🇮🇹'],['Türkçe','TR','🇹🇷'],
  ['Қазақша','KK','🇰🇿'],['Français','FR','🇫🇷'],['Deutsch','DE','🇩🇪'],['한국어','KO','🇰🇷'],['简体中文','ZH','🇨🇳']
];

export default function AcademyPreview(){
  return <main className="student-app">
    <aside className="student-sidebar">
      <Link href="/academy" className="student-brand">AIRA<span>Academy</span></Link>
      <nav className="student-nav">
        <Link className="active" href="/academy">⌂ <span>Главная</span></Link>
        <Link href="/learn">◇ <span>Обучение</span></Link>
        <Link href="/learn/catalog">◎ <span>Языки</span></Link>
        <Link href="/learn/tutor">✦ <span>AIRA Tutor</span></Link>
        <Link href="/learn/progress">↗ <span>Прогресс</span></Link>
      </nav>
      <div className="student-sidebar-bottom"><p className="student-mini-label">AIRA ACADEMY</p><Link href="/developer">Кабинет основателя</Link></div>
    </aside>
    <section className="student-content">
      <header className="student-topbar"><div><p className="student-mini-label">AIRA ACADEMY</p><strong>Персональное изучение языков.</strong></div><div className="student-profile"><span>Серия: 7 дней</span><b>A</b></div></header>
      <div className="student-page">
        <section className="student-welcome"><div><p className="student-mini-label">С ВОЗВРАЩЕНИЕМ</p><h1>Готова к следующему уроку?</h1><p>AIRA адаптирует уроки, объяснения и практику под язык, который тебе уже понятен.</p></div><div className="student-streak"><span>🔥</span><strong>7</strong><small>дней подряд</small></div></section>
        <section className="continue-card"><div className="course-badge" style={{fontSize:'26px'}}>🇺🇸</div><div className="continue-copy"><p className="student-mini-label">ПРОДОЛЖИТЬ ОБУЧЕНИЕ</p><h2>English · Начальный уровень</h2><p>Повседневный разговор · Урок 4 из 12</p><div className="progress-track"><span style={{width:'32%'}} /></div><small>Пройдено 32%</small></div><Link href="/learn/courses" className="student-primary">Продолжить урок →</Link></section>
        <div className="student-section-head"><div><p className="student-mini-label">ОБУЧАЙСЯ С AIRA</p><h2>Инструменты обучения</h2></div></div>
        <section className="learning-tools"><article className="learning-tool featured"><span className="tool-icon">✦</span><h3>AIRA Tutor</h3><p>Задавай вопросы и получай объяснения на понятном тебе языке.</p><Link href="/learn/tutor">Начать диалог →</Link></article><article className="learning-tool"><span className="tool-icon">◉</span><h3>Voice Tutor</h3><p>Практикуй разговор, произношение и понимание речи.</p><Link href="/learn/tutor">Открыть практику →</Link></article><article className="learning-tool"><span className="tool-icon">▶</span><h3>Видеоуроки</h3><p>Короткие уроки с AIRA, адаптированные под твой текущий уровень.</p><Link href="/learn/courses">Открыть учебный путь →</Link></article></section>
        <div className="student-section-head"><div><p className="student-mini-label">КАТАЛОГ ЯЗЫКОВ</p><h2>Выбери язык для обучения</h2></div><Link href="/learn/catalog">Все языки →</Link></div>
        <section className="student-language-grid">{languages.map(([name,code,flag])=><Link className="student-language" href="/learn/catalog" key={code}><span aria-label={`${name} flag`} style={{fontSize:'24px',background:'transparent'}}>{flag}</span><div><strong>{name}</strong><small>Персональный учебный путь</small></div><b>→</b></Link>)}</section>
        <section className="student-progress-card"><div><p className="student-mini-label">ТВОЙ ПРОГРЕСС</p><h2>Небольшие шаги приводят к свободной речи.</h2><p>Уроки, Tutor, Voice и видео будут объединяться в единую историю обучения.</p><Link href="/learn/progress">Подробный прогресс →</Link></div><div className="progress-stats"><div><strong>4</strong><span>урока</span></div><div><strong>32%</strong><span>текущий курс</span></div><div><strong>7</strong><span>дней подряд</span></div></div></section>
      </div>
    </section>
  </main>
}
