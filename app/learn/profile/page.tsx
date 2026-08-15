"use client";

import { useEffect, useState } from "react";
import styles from "../learn.module.css";
import { DEFAULT_LEARNER_PROFILE, LearnerProfile, loadLearnerProfile, saveLearnerProfile } from "../../../lib/learner-profile";
import { useUiLanguage } from "../../../lib/use-ui-language";

export default function Profile(){
  const ru=useUiLanguage()==="ru";
  const [profile,setProfile]=useState<LearnerProfile>(DEFAULT_LEARNER_PROFILE); const [saved,setSaved]=useState(false);
  useEffect(()=>setProfile(loadLearnerProfile()),[]);
  function update<K extends keyof LearnerProfile>(key:K,value:LearnerProfile[K]){setSaved(false);setProfile(current=>({...current,[key]:value}));}
  function save(){saveLearnerProfile(profile);setSaved(true);}
  return <><div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"ПРОФИЛЬ":"PROFILE"}</span><h1>{ru?"Учебный профиль":"Learning profile"}</h1><p>{ru?"Язык, уровень и цели помогают AIRA строить персональный учебный маршрут.":"Your language, level and goals shape the personalized AIRA learning path."}</p></div><form className={styles.formCard} onSubmit={event=>{event.preventDefault();save();}}><label>{ru?"Язык объяснений":"Explanation language"}<input value={profile.nativeLanguage} onChange={event=>update("nativeLanguage",event.target.value)} /></label><label>{ru?"Изучаемый язык":"Target language"}<input value={profile.targetLanguage} onChange={event=>update("targetLanguage",event.target.value)} /></label><div className={styles.formGrid}><label>{ru?"Текущий уровень":"Current level"}<select value={profile.currentLevel} onChange={event=>update("currentLevel",event.target.value)}><option>A1</option><option>A2</option><option>B1</option><option>B2</option></select></label><label>{ru?"Целевой уровень":"Target level"}<select value={profile.targetLevel} onChange={event=>update("targetLevel",event.target.value)}><option>A2</option><option>B1</option><option>B2</option></select></label></div><label>{ru?"Цели обучения":"Learning goals"}<textarea value={profile.learningGoals} onChange={event=>update("learningGoals",event.target.value)} /></label><label>{ru?"Цель на день":"Daily target"}<input type="number" min={5} max={180} value={profile.dailyTarget} onChange={event=>update("dailyTarget",Number(event.target.value))}/></label><button className={styles.primaryButton} type="submit">{ru?"Сохранить профиль":"Save profile"}</button>{saved && <p>{ru?"✓ Профиль сохранён. AIRA будет использовать эти настройки на этом устройстве.":"✓ Profile saved. AIRA will use these preferences across the learning experience on this device."}</p>}</form></>;
}
