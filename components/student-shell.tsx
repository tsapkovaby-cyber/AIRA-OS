"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "../app/learn/learn.module.css";
import { getUiLanguage, setUiLanguage, type UiLanguage } from "../lib/ui-language";

const nav = {
  ru: [["/learn", "Главная"],["/learn/courses", "Моё обучение"],["/learn/catalog", "Курсы"],["/learn/progress", "Прогресс"],["/learn/tutor", "AIRA Tutor"],["/learn/profile", "Профиль"],["/learn/settings", "Настройки"]],
  en: [["/learn", "Dashboard"],["/learn/courses", "My Learning"],["/learn/catalog", "Courses"],["/learn/progress", "Progress"],["/learn/tutor", "AIRA Tutor"],["/learn/profile", "Profile"],["/learn/settings", "Settings"]],
} as const;

export function StudentShell({ children }: { children: React.ReactNode }) {
  const [language,setLanguage]=useState<UiLanguage>("ru");
  useEffect(()=>{setLanguage(getUiLanguage());},[]);
  const changeLanguage=(value:UiLanguage)=>{setLanguage(value);setUiLanguage(value);};
  const ru=language==="ru";
  return <div className={styles.shell}>
    <aside className={styles.sidebar}>
      <Link className={styles.brand} href="/learn"><span className={styles.brandMark}>A</span><span>AIRA <small>Academy</small></span></Link>
      <nav className={styles.nav} aria-label={ru?"Навигация ученика":"Student navigation"}>{nav[language].map(([href,label])=><Link key={href} href={href}>{label}</Link>)}</nav>
      <div className={styles.sidebarCard}><strong>{ru?"Цель на день":"Daily goal"}</strong><span>20 {ru?"мин":"min"}</span><div className={styles.miniBar}><i /></div><small>{ru?"Сохраняй регулярность обучения":"Keep your streak alive"}</small></div>
    </aside>
    <div className={styles.main}><header className={styles.topbar}><div><span className={styles.eyebrow}>{ru?"УЧЕБНАЯ ПЛАТФОРМА AIRA":"AIRA LEARNING PLATFORM"}</span></div><div className={styles.topActions}><select aria-label={ru?"Язык приложения":"Application language"} value={language} onChange={e=>changeLanguage(e.target.value as UiLanguage)}><option value="ru">Русский</option><option value="en">English</option></select><button aria-label={ru?"Уведомления":"Notifications"}>◌</button><div className={styles.avatar}>K</div></div></header><main className={styles.content}>{children}</main></div>
  </div>;
}
