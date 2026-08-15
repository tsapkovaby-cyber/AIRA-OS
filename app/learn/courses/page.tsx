import Link from "next/link";
import styles from "../learn.module.css";

const languageNames: Record<string,string> = {EN:"English",RU:"Русский",ES:"Español",IT:"Italiano",TR:"Türkçe",KK:"Қазақша",FR:"Français",DE:"Deutsch",KO:"한국어",ZH:"简体中文"};
const flags: Record<string,string> = {EN:"🇺🇸",RU:"🇷🇺",ES:"🇪🇸",IT:"🇮🇹",TR:"🇹🇷",KK:"🇰🇿",FR:"🇫🇷",DE:"🇩🇪",KO:"🇰🇷",ZH:"🇨🇳"};

export default function MyLearning({searchParams}:{searchParams?:{lang?:string;level?:string}}){
  const lang=(searchParams?.lang||"EN").toUpperCase();
  const level=(searchParams?.level||"A1").toUpperCase();
  const name=languageNames[lang]||"English";
  const flag=flags[lang]||"🇺🇸";
  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>STEP 3 · YOUR LEARNING PATH</span><h1>{flag} {name} · {level}</h1><p>Your course path is organized into short lessons, practice and AIRA Tutor support. Progress will update as you complete each step.</p></div>
    <div className={styles.courseGrid}>
      <article className={styles.courseCard}><span className={styles.pill}>{name} · {level}</span><h2>Everyday conversation</h2><p>Build practical speaking confidence through introductions, common questions and daily situations.</p><div className={styles.progress}><i style={{width:"25%"}} /></div><small>Lesson 1 of 4 · next: Introducing yourself</small><Link className={styles.primaryButton} href={`/learn/lesson?lang=${lang}&level=${level}`}>Start lesson 1</Link></article>
      <article className={styles.courseCard}><span className={styles.pill}>Practice</span><h2>Conversation practice</h2><p>Use AIRA Tutor to rehearse what you learn, get corrections and repeat difficult phrases.</p><Link className={styles.secondaryButton} href={`/learn/practice?lang=${lang}&level=${level}`}>Open practice</Link></article>
    </div>
    <div className={styles.section}><Link className={styles.textLink} href={`/learn/level?lang=${lang}`}>← Change level</Link></div>
  </>
}
