import Link from "next/link";
import styles from "../learn.module.css";

const languageNames: Record<string,string> = {EN:"English",RU:"Русский",ES:"Español",IT:"Italiano",TR:"Türkçe",KK:"Қазақша",FR:"Français",DE:"Deutsch",KO:"한국어",ZH:"简体中文"};
const flags: Record<string,string> = {EN:"🇺🇸",RU:"🇷🇺",ES:"🇪🇸",IT:"🇮🇹",TR:"🇹🇷",KK:"🇰🇿",FR:"🇫🇷",DE:"🇩🇪",KO:"🇰🇷",ZH:"🇨🇳"};
const levels = [
  ["A1","Beginner","Start from zero: greetings, introductions, basic everyday phrases."],
  ["A2","Elementary","Build everyday vocabulary and handle simple real-life situations."],
  ["B1","Intermediate","Speak more freely, understand common conversations and express opinions."],
  ["B2","Upper intermediate","Develop confident, flexible communication for work, travel and daily life."],
] as const;

export default function LevelSelection({searchParams}:{searchParams?:{lang?:string}}){
  const lang=(searchParams?.lang||"EN").toUpperCase();
  const name=languageNames[lang]||"English";
  const flag=flags[lang]||"🇺🇸";
  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>STEP 2 · CHOOSE YOUR LEVEL</span><h1>{flag} {name}</h1><p>Select the level that feels closest to your current ability. AIRA can later adjust it after a placement check.</p></div>
    <div className={styles.courseGrid}>{levels.map(([level,title,description])=><article className={styles.courseCard} key={level}><span className={styles.pill}>{level}</span><h2>{title}</h2><p>{description}</p><Link className={styles.primaryButton} href={`/learn/courses?lang=${lang}&level=${level}`}>Choose {level}</Link></article>)}</div>
    <div className={styles.section}><Link className={styles.textLink} href="/learn/catalog">← Back to languages</Link></div>
  </>
}
