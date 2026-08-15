import Link from "next/link";
import styles from "../learn.module.css";

const languages = [
  ["English","EN","🇺🇸","Conversational English","A1–B2","Active"],
  ["Русский","RU","🇷🇺","Conversational Russian","A1–B2","Available"],
  ["Español","ES","🇪🇸","Conversational Spanish","A1–B2","Available"],
  ["Italiano","IT","🇮🇹","Conversational Italian","A1–B2","Available"],
  ["Türkçe","TR","🇹🇷","Conversational Turkish","A1–B2","Available"],
  ["Қазақша","KK","🇰🇿","Conversational Kazakh","A1–B2","Available"],
  ["Français","FR","🇫🇷","Conversational French","A1–B2","Available"],
  ["Deutsch","DE","🇩🇪","Conversational German","A1–B2","Available"],
  ["한국어","KO","🇰🇷","Conversational Korean","A1–B2","Available"],
  ["简体中文","ZH","🇨🇳","Conversational Chinese","A1–B2","Available"],
] as const;

export default function Catalog(){return <>
  <div className={styles.pageHeading}><span className={styles.eyebrow}>LANGUAGE CATALOG</span><h1>Choose your learning language</h1><p>Learn in the explanation language you already understand. Every language follows the same personal path structure and can later adapt to your goals.</p></div>
  <div className={styles.courseGrid}>{languages.map(([name,code,flag,title,levels,state])=><article className={styles.courseCard} key={code}><span style={{fontSize:'30px'}} aria-label={`${name} flag`}>{flag}</span><span className={styles.pill}>{code} · {levels}</span><h2>{name}</h2><p>{title}. Start from the right level, practice everyday speech and build toward confident independent use.</p>{state==="Active"?<Link className={styles.primaryButton} href="/learn/courses">Continue current path</Link>:<button className={styles.secondaryButton}>Choose language</button>}</article>)}</div>
</>}
