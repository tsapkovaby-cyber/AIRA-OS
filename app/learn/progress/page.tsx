"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "../learn.module.css";
import { DEFAULT_LEARNER_PROFILE, LearnerProfile, loadLearnerProfile } from "../../../lib/learner-profile";
import { useUiLanguage } from "../../../lib/use-ui-language";

export default function Progress(){
  const ru=useUiLanguage()==="ru";
  const [profile,setProfile]=useState<LearnerProfile>(DEFAULT_LEARNER_PROFILE);
  useEffect(()=>setProfile(loadLearnerProfile()),[]);
  const totalLessons=12; const completed=profile.completedLessons.length; const completion=useMemo(()=>Math.min(100,Math.round((completed/totalLessons)*100)),[completed]);
  return <><div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"ПРОГРЕСС":"PROGRESS"}</span><h1>{ru?"Твой прогресс обучения":"Your learning progress"}</h1><p>{ru?"Следи за регулярностью, прохождением курса и учебным маршрутом, который AIRA формирует вокруг твоих целей.":"Track consistency, course completion and the learning path AIRA is building around you."}</p></div><div className={styles.statsGrid}><article><span>{ru?"Общий прогресс":"Overall progress"}</span><strong>{completion}%</strong><small>{profile.targetLanguage} {profile.currentLevel}</small></article><article><span>{ru?"Завершённые уроки":"Completed lessons"}</span><strong>{completed}</strong><small>{ru?`Осталось уроков: ${Math.max(0,totalLessons-completed)}`:`${Math.max(0,totalLessons-completed)} lessons remaining`}</small></article><article><span>{ru?"Текущая серия":"Current streak"}</span><strong>{profile.streak} {ru?"дн.":profile.streak===1?"day":"days"}</strong><small>{profile.lastActivityAt?(ru?"Последняя активность сохранена":"Recent learning activity saved"):(ru?"Заверши первый урок":"Complete your first lesson")}</small></article><article><span>{ru?"Цель на день":"Daily target"}</span><strong>{profile.dailyTarget} {ru?"мин":"min"}</strong><small>{ru?"Персональная учебная цель":"Personal learning goal"}</small></article></div><article className={styles.panel}><h2>{ru?"Прохождение курса":"Course completion"}</h2><div className={styles.progressRow}><div className={styles.progress}><i style={{width:`${completion}%`}}/></div><span>{completion}%</span></div><p className={styles.muted}>{ru?`Текущий путь: ${profile.targetLanguage} · ${profile.currentLevel} → ${profile.targetLevel}. История уроков и настройки профиля объединены в одной записи ученика на этом устройстве.`:`Current path: ${profile.targetLanguage} · ${profile.currentLevel} → ${profile.targetLevel}. Lesson history and profile preferences share one learner record on this device.`}</p></article></>;
}
