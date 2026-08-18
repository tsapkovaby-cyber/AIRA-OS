"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "../learn.module.css";
import { getUiLanguage, setUiLanguage, type UiLanguage } from "../../../lib/ui-language";
import { LearnerAccountStatus, loadLearnerAccountStatus, signOutLearner } from "../../../lib/learner-account";
import { LearnerSyncState, clearLearnerAccountLink, hydrateLearnerProfileFromAccount, loadLearnerSyncState, subscribeLearnerSyncState } from "../../../lib/learner-profile";

const EMPTY_ACCOUNT: LearnerAccountStatus = { authConfigured:false, storageConfigured:false, authenticated:false, user:null };

export default function Settings(){
  const router=useRouter();
  const [language,setLanguage]=useState<UiLanguage>("ru");
  const [account,setAccount]=useState<LearnerAccountStatus>(EMPTY_ACCOUNT);
  const [sync,setSync]=useState<LearnerSyncState>({status:"local",lastSyncedAt:null,accountLinked:false});
  const [busy,setBusy]=useState(false);
  useEffect(()=>{
    setLanguage(getUiLanguage());
    setSync(loadLearnerSyncState());
    void loadLearnerAccountStatus().then(setAccount);
    return subscribeLearnerSyncState(setSync);
  },[]);
  const ru=language==="ru";
  function changeLanguage(value:UiLanguage){setLanguage(value);setUiLanguage(value);}
  async function restore(){setBusy(true);await hydrateLearnerProfileFromAccount();setSync(loadLearnerSyncState());setBusy(false);}
  async function logout(){setBusy(true);await signOutLearner();clearLearnerAccountLink();setAccount(await loadLearnerAccountStatus());setSync(loadLearnerSyncState());setBusy(false);router.refresh();}
  const syncText = sync.status==="synced" ? (ru?"Синхронизировано":"Synced") : sync.status==="syncing" ? (ru?"Синхронизация…":"Syncing…") : sync.status==="error" ? (ru?"Ошибка синхронизации":"Sync error") : (ru?"Локальное хранение":"Local storage");

  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"НАСТРОЙКИ":"SETTINGS"}</span><h1>{ru?"Аккаунт, язык и конфиденциальность":"Account, language & privacy"}</h1><p>{ru?"Настрой язык приложения, облачную синхронизацию и безопасность аккаунта.":"Manage application language, cloud sync and account safety."}</p></div>
    <div className={styles.settingsList}>
      <article><div><h3>{ru?"Язык приложения":"Application language"}</h3><p>{ru?"Интерфейс Academy будет отображаться на выбранном языке. Язык обучения и язык объяснений настраиваются отдельно в профиле.":"Academy interface uses this language. Learning and explanation languages remain separate profile preferences."}</p></div><select value={language} onChange={e=>changeLanguage(e.target.value as UiLanguage)}><option value="ru">Русский</option><option value="en">English</option></select></article>
      <article><div><h3>{ru?"Аккаунт ученика":"Student account"}</h3><p>{account.authenticated ? `${ru?"Выполнен вход":"Signed in"}: ${account.user?.email || account.user?.id}` : account.authConfigured ? (ru?"Аккаунт не подключён. Можно продолжать локально или войти для синхронизации.":"No account is connected. Continue locally or sign in for sync.") : (ru?"Supabase Auth пока не настроен. Обучение продолжает работать локально.":"Supabase Auth is not configured yet. Learning continues locally.")}</p></div>{account.authenticated?<Link className={styles.secondaryButton} href="/learn/profile">{ru?"Профиль":"Profile"}</Link>:<Link className={styles.secondaryButton} href="/learn/sign-in">{ru?"Войти":"Sign in"}</Link>}</article>
      <article><div><h3>{ru?"Облачная синхронизация":"Cloud sync"}</h3><p>{syncText}{sync.lastSyncedAt?` · ${new Date(sync.lastSyncedAt).toLocaleString(ru?"ru-RU":"en-US")}`:""}. {account.storageConfigured?(ru?"Серверное хранилище доступно.":"Server storage is available."):(ru?"Серверное хранилище пока не настроено.":"Server storage is not configured yet.")}</p></div><button className={styles.secondaryButton} disabled={!account.authenticated||busy} onClick={restore}>{busy?(ru?"Подождите…":"Please wait…"):(ru?"Восстановить":"Restore")}</button></article>
      <article><div><h3>{ru?"Безопасность аккаунта":"Account security"}</h3><p>{ru?"Сессия ученика хранится в защищённых HTTP-only cookies. Пароль не сохраняется в браузере Academy.":"Student sessions use protected HTTP-only cookies. Academy does not store the password in the browser."}</p></div><span>{account.authenticated?(ru?"Сессия активна":"Session active"):(ru?"Нет активной сессии":"No active session")}</span></article>
      <article><div><h3>{ru?"Конфиденциальность":"Privacy"}</h3><p>{ru?"Учебные данные привязаны к аккаунту только после входа. В локальном режиме данные остаются на устройстве.":"Learning data is linked to an account only after sign-in. In local mode, data stays on the device."}</p></div><Link className={styles.secondaryButton} href="/learn/profile">{ru?"Проверить профиль":"Review profile"}</Link></article>
      <article><div><h3>{ru?"Выйти":"Sign out"}</h3><p>{account.authenticated?(ru?"Завершить текущую облачную сессию. Локальный учебный профиль на устройстве останется доступен.":"End the current cloud session. The local learning profile remains available on this device."):(ru?"Сейчас вход в аккаунт не выполнен.":"You are not currently signed in.")}</p></div><button className={styles.secondaryButton} disabled={!account.authenticated||busy} onClick={logout}>{ru?"Выйти":"Sign out"}</button></article>
    </div>
  </>;
}
