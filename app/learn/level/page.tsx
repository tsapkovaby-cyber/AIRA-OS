"use client";

import Link from "next/link";
import styles from "../learn.module.css";
import { useUiLanguage } from "../../../lib/use-ui-language";

const languageNames: Record<string,string> = {EN:"English",RU:"Русский",ES:"Español",IT:"Italiano",TR:"Türkçe",KK:"Қазақша",FR:"Français",DE:"Deutsch",KO:"한국어",ZH:"简体中文"};
const flags: Record<string,string> = {EN:"🇺🇸",RU:"🇷🇺",ES:"🇪🇸",IT:"🇮🇹",TR:"🇹🇷",KK:"🇰🇿",FR:"🇫🇷",DE:"🇩🇪",KO:"🇰🇷",ZH:"🇨🇳"};
const levels = [
  ["A1","Начальный","Beginner","Начни с нуля: приветствия, знакомство и базовые повседневные фразы.","Start from zero: greetings, introductions and basic everyday phrases."],
  ["A2","Базовый","Elementary","Расширяй словарный запас и уверенно справляйся с простыми бытовыми ситуациями.","Build everyday vocabulary and handle simple real-life situations."],
  ["B1","Средний","Intermediate","Говори свободнее, понимай обычные разговоры и выражай своё мнение.","Speak more freely, understand common conversations and express opinions."],
  ["B2","Выше среднего","Upper intermediate","Развивай уверенное и гибкое общение для работы, путешествий и жизни.","Develop confident, flexible communication for work, travel and daily life."],
] as const;

export default function LevelSelection({searchParams}:{searchParams?:{lang?:string}}){
  const ru=useUiLanguage()==="ru";
  const lang=(searchParams?.lang||"EN").toUpperCase(); const name=languageNames[lang]||"English"; const flag=flags[lang]||"🇺🇸";
  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"ШАГ 2 · ВЫБОР УРОВНЯ":"STEP 2 · CHOOSE YOUR LEVEL"}</span><h1>{flag} {name}</h1><p>{ru?"Выбери уровень, который ближе всего к твоим текущим знаниям. Позже AIRA сможет уточнить его с помощью короткого теста.":"Select the level closest to your current ability. AIRA can refine it later with a short placement check."}</p></div>
    <div className={styles.courseGrid}>{levels.map(([level,ruTitle,enTitle,ruDesc,enDesc])=><article className={styles.courseCard} key={level}><span className={styles.pill}>{level}</span><h2>{ru?ruTitle:enTitle}</h2><p>{ru?ruDesc:enDesc}</p><Link className={styles.primaryButton} href={`/learn/courses?lang=${lang}&level=${level}`}>{ru?`Выбрать ${level}`:`Choose ${level}`}</Link></article>)}</div>
    <div className={styles.section}><Link className={styles.textLink} href="/learn/catalog">← {ru?"Назад к языкам":"Back to languages"}</Link></div>
  </>;
}
