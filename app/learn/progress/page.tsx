"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "../learn.module.css";
import { DEFAULT_LEARNER_PROFILE, LearnerProfile, loadLearnerProfile } from "../../../lib/learner-profile";

export default function Progress(){
  const [profile,setProfile]=useState<LearnerProfile>(DEFAULT_LEARNER_PROFILE);
  useEffect(()=>setProfile(loadLearnerProfile()),[]);
  const totalLessons=12;
  const completed=profile.completedLessons.length;
  const completion=useMemo(()=>Math.min(100,Math.round((completed/totalLessons)*100)),[completed]);

  return <><div className={styles.pageHeading}><span className={styles.eyebrow}>PROGRESS</span><h1>Your learning progress</h1><p>Track consistency, course completion and the learning path AIRA is building around you.</p></div><div className={styles.statsGrid}><article><span>Overall progress</span><strong>{completion}%</strong><small>{profile.targetLanguage} {profile.currentLevel}</small></article><article><span>Completed lessons</span><strong>{completed}</strong><small>{Math.max(0,totalLessons-completed)} lessons remaining</small></article><article><span>Current streak</span><strong>{profile.streak} {profile.streak===1?"day":"days"}</strong><small>{profile.lastActivityAt?"Recent learning activity saved":"Complete your first lesson"}</small></article><article><span>Daily target</span><strong>{profile.dailyTarget} min</strong><small>Personal learning goal</small></article></div><article className={styles.panel}><h2>Course completion</h2><div className={styles.progressRow}><div className={styles.progress}><i style={{width:`${completion}%`}}/></div><span>{completion}%</span></div><p className={styles.muted}>Current path: {profile.targetLanguage} · {profile.currentLevel} → {profile.targetLevel}. Completed lesson history and profile preferences now share one learner record on this device.</p></article></>}
