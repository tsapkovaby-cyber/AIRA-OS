"use client";

import Link from "next/link";
import styles from "../learn.module.css";
import { useUiLanguage } from "../../../lib/use-ui-language";

const languageNames: Record<string,string> = {EN:"English",RU:"Русский",ES:"Español",IT:"Italiano",TR:"Türkçe",KK:"Қазақша",FR:"Français",DE:"Deutsch",KO:"한국어",ZH:"简体中文"};
const flags: Record<string,string> = {EN:"🇺🇸",RU:"🇷🇺",ES:"🇪🇸",IT:"🇮🇹",TR:"🇹🇷",KK:"🇰🇿",FR:"🇫🇷",DE:"🇩🇪",KO:"🇰🇷",ZH:"🇨🇳"};

export default function MyLearning({searchParams}:{searchParams?:{lang?:string;level?:string}}){
  const ru=useUiLanguage()==="ru";
  const lang=(searchParams?.lang||"EN").toUpperCase(); const level=(searchParams?.level||"A1").toUpperCase(); const name=languageNames[lang]||"English"; const flag=flags[lang]||"🇺🇸";
  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"ШАГ 3 · ТВОЙ УЧЕБНЫЙ ПУТЬ":"STEP 3 · YOUR LEARNING PATH"}</span><h1>{flag} {name} · {level}</h1><p>{ru?"Курс разбит на короткие уроки, практику и поддержку AIRA Tutor. Прогресс обновляется после каждого завершённого шага.":"Your course path is organized into short lessons, practice and AIRA Tutor support. Progress updates as you complete each step."}</p></div>
    <div className={styles.courseGrid}>
      <article className={styles.courseCard}><span className={styles.pill}>{name} · {level}</span><h2>{ru?"Повседневное общение":"Everyday conversation"}</h2><p>{ru?"Развивай разговорную уверенность через знакомства, обычные вопросы и реальные бытовые ситуации.":"Build speaking confidence through introductions, common questions and real-life situations."}</p><div className={styles.progress}><i style={{width:"25%"}} /></div><small>{ru?"Урок 1 из 4 · далее: знакомство и рассказ о себе":"Lesson 1 of 4 · next: Introducing yourself"}</small><Link className={styles.primaryButton} href={`/learn/lesson?lang=${lang}&level=${level}`}>{ru?"Начать урок 1":"Start lesson 1"}</Link></article>
      <article className={styles.courseCard}><span className={styles.pill}>{ru?"Практика":"Practice"}</span><h2>{ru?"Разговорная практика":"Conversation practice"}</h2><p>{ru?"Тренируй пройденное с AIRA Tutor, получай исправления и повторяй сложные фразы.":"Use AIRA Tutor to rehearse what you learn, get corrections and repeat difficult phrases."}</p><Link className={styles.secondaryButton} href={`/learn/practice?lang=${lang}&level=${level}`}>{ru?"Открыть практику":"Open practice"}</Link></article>
    </div>
    <div className={styles.section}><Link className={styles.textLink} href={`/learn/level?lang=${lang}`}>← {ru?"Изменить уровень":"Change level"}</Link></div>
  </>;
}
