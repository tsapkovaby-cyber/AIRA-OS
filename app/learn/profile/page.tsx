"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "../learn.module.css";
import { DEFAULT_LEARNER_PROFILE, LearnerProfile, LearnerSyncState, hydrateLearnerProfileFromAccount, loadLearnerProfile, loadLearnerSyncState, saveLearnerProfile, subscribeLearnerSyncState } from "../../../lib/learner-profile";
import { LearnerAccountStatus, loadLearnerAccountStatus } from "../../../lib/learner-account";
import { useUiLanguage } from "../../../lib/use-ui-language";

const EMPTY_ACCOUNT: LearnerAccountStatus = { authConfigured:false, storageConfigured:false, authenticated:false, user:null };

export default function Profile(){
  const ru=useUiLanguage()==="ru";
  const [profile,setProfile]=useState<LearnerProfile>(DEFAULT_LEARNER_PROFILE);
  const [saved,setSaved]=useState(false);
  const [account,setAccount]=useState<LearnerAccountStatus>(EMPTY_ACCOUNT);
  const [sync,setSync]=useState<LearnerSyncState>({status:"local",lastSyncedAt:null,accountLinked:false});

  useEffect(()=>{
    setProfile(loadLearnerProfile());
    setSync(loadLearnerSyncState());
    void loadLearnerAccountStatus().then(setAccount);
    return subscribeLearnerSyncState(setSync);
  },[]);

  function update<K extends keyof LearnerProfile>(key:K,value:LearnerProfile[K]){setSaved(false);setProfile(current=>({...current,[key]:value}));}
  function save(){saveLearnerProfile(profile);setSaved(true);}
  async function restore(){const cloud=await hydrateLearnerProfileFromAccount();if(cloud){setProfile(cloud);setSaved(false);}setSync(loadLearnerSyncState());}

  const syncLabel = sync.status==="synced" ? (ru?"Синхронизировано":"Synced") : sync.status==="syncing" ? (ru?"Синхронизация…":"Syncing…") : sync.status==="error" ? (ru?"Ошибка синхронизации":"Sync error") : (ru?"Только на устройстве":"Local only");

  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"ПРОФИЛЬ":"PROFILE"}</span><h1>{ru?"Учебный профиль":"Learning profile"}</h1><p>{ru?"Язык, уровень и цели помогают AIRA строить персональный учебный маршрут.":"Your language, level and goals shape the personalized AIRA learning path."}</p></div>

    <div className={styles.settingsList} style={{marginBottom:20}}>
      <article><div><h3>{ru?"Аккаунт ученика":"Student account"}</h3><p>{account.authenticated ? `${account.user?.email || (ru?"Аккаунт подключён":"Account connected")}` : (ru?"Сейчас обучение работает локально на этом устройстве.":"Learning is currently local to this device.")}</p></div>{account.authenticated?<Link className={styles.secondaryButton} href="/learn/settings">{ru?"Управление":"Manage"}</Link>:<Link className={styles.secondaryButton} href="/learn/sign-in">{ru?"Войти":"Sign in"}</Link>}</article>
      <article><div><h3>{ru?"Облачная синхронизация":"Cloud sync"}</h3><p>{syncLabel}{sync.lastSyncedAt?` · ${new Date(sync.lastSyncedAt).toLocaleString(ru?"ru-RU":"en-US")}`:""}</p></div>{account.authenticated?<button className={styles.secondaryButton} type="button" onClick={restore}>{ru?"Восстановить из облака":"Restore from cloud"}</button>:<span>{account.storageConfigured?(ru?"Нужен вход":"Sign in required"):(ru?"Хранилище не подключено":"Storage not configured")}</span>}</article>
    </div>

    <form className={styles.formCard} onSubmit={event=>{event.preventDefault();save();}}><label>{ru?"Язык объяснений":"Explanation language"}<input value={profile.nativeLanguage} onChange={event=>update("nativeLanguage",event.target.value)} /></label><label>{ru?"Изучаемый язык":"Target language"}<input value={profile.targetLanguage} onChange={event=>update("targetLanguage",event.target.value)} /></label><div className={styles.formGrid}><label>{ru?"Текущий уровень":"Current level"}<select value={profile.currentLevel} onChange={event=>update("currentLevel",event.target.value)}><option>A1</option><option>A2</option><option>B1</option><option>B2</option></select></label><label>{ru?"Целевой уровень":"Target level"}<select value={profile.targetLevel} onChange={event=>update("targetLevel",event.target.value)}><option>A2</option><option>B1</option><option>B2</option></select></label></div><label>{ru?"Цели обучения":"Learning goals"}<textarea value={profile.learningGoals} onChange={event=>update("learningGoals",event.target.value)} /></label><label>{ru?"Цель на день":"Daily target"}<input type="number" min={5} max={180} value={profile.dailyTarget} onChange={event=>update("dailyTarget",Number(event.target.value))}/></label><button className={styles.primaryButton} type="submit">{ru?"Сохранить профиль":"Save profile"}</button>{saved && <p>{account.authenticated?(ru?"✓ Профиль сохранён. Облачная синхронизация запущена.":"✓ Profile saved. Cloud sync started."):(ru?"✓ Профиль сохранён на этом устройстве.":"✓ Profile saved on this device.")}</p>}</form>
  </>;
}
