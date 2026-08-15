"use client";

import Link from "next/link";
import styles from "../learn.module.css";
import { useUiLanguage } from "../../../lib/use-ui-language";

const languages = [
  ["English","EN","🇺🇸","Английский для общения","Conversational English"],
  ["Русский","RU","🇷🇺","Русский для общения","Conversational Russian"],
  ["Español","ES","🇪🇸","Испанский для общения","Conversational Spanish"],
  ["Italiano","IT","🇮🇹","Итальянский для общения","Conversational Italian"],
  ["Türkçe","TR","🇹🇷","Турецкий для общения","Conversational Turkish"],
  ["Қазақша","KK","🇰🇿","Казахский для общения","Conversational Kazakh"],
  ["Français","FR","🇫🇷","Французский для общения","Conversational French"],
  ["Deutsch","DE","🇩🇪","Немецкий для общения","Conversational German"],
  ["한국어","KO","🇰🇷","Корейский для общения","Conversational Korean"],
  ["简体中文","ZH","🇨🇳","Китайский для общения","Conversational Chinese"],
] as const;

export default function Catalog(){
  const ru=useUiLanguage()==="ru";
  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"ШАГ 1 · КАТАЛОГ ЯЗЫКОВ":"STEP 1 · LANGUAGE CATALOG"}</span><h1>{ru?"Выбери язык для изучения":"Choose your learning language"}</h1><p>{ru?"Выбирай язык, а AIRA поможет определить подходящий стартовый уровень и построит персональный путь обучения.":"Choose a language and AIRA will help you select the right starting level and build a personal learning path."}</p></div>
    <div className={styles.courseGrid}>{languages.map(([name,code,flag,ruTitle,enTitle])=><article className={styles.courseCard} key={code}><span style={{fontSize:'30px'}}>{flag}</span><span className={styles.pill}>{code} · A1–B2</span><h2>{name}</h2><p>{ru?`${ruTitle}. Начни с подходящего уровня, тренируй повседневную речь и двигайся к уверенному самостоятельному общению.`:`${enTitle}. Start at the right level, practice everyday speech and build toward confident independent use.`}</p><Link className={code==="EN"?styles.primaryButton:styles.secondaryButton} href={`/learn/level?lang=${code}`}>{ru?"Выбрать язык":"Choose language"}</Link></article>)}</div>
  </>;
}
