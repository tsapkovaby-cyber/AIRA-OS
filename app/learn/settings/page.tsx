"use client";

import { useEffect, useState } from "react";
import styles from "../learn.module.css";
import { getUiLanguage, setUiLanguage, type UiLanguage } from "../../../lib/ui-language";

export default function Settings(){
  const [language,setLanguage]=useState<UiLanguage>("ru");
  useEffect(()=>setLanguage(getUiLanguage()),[]);
  const ru=language==="ru";
  function changeLanguage(value:UiLanguage){setLanguage(value);setUiLanguage(value);}
  return <>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>{ru?"НАСТРОЙКИ":"SETTINGS"}</span><h1>{ru?"Аккаунт, язык и конфиденциальность":"Account, language & privacy"}</h1><p>{ru?"Настрой язык приложения, обучение и безопасность аккаунта.":"Manage your application language, learning preferences and account safety."}</p></div>
    <div className={styles.settingsList}>
      <article><div><h3>{ru?"Язык приложения":"Application language"}</h3><p>{ru?"Интерфейс Academy будет отображаться на выбранном языке. Язык обучения и язык объяснений настраиваются отдельно в профиле.":"Academy interface uses this language. Learning and explanation languages remain separate profile preferences."}</p></div><select value={language} onChange={e=>changeLanguage(e.target.value as UiLanguage)}><option value="ru">Русский</option><option value="en">English</option></select></article>
      <article><div><h3>{ru?"Безопасность аккаунта":"Account security"}</h3><p>{ru?"Пароль и активные сессии будут управляться через систему аккаунтов ученика.":"Password and active sessions are managed through the student account domain."}</p></div><button className={styles.secondaryButton}>{ru?"Управление":"Manage"}</button></article>
      <article><div><h3>{ru?"Конфиденциальность":"Privacy"}</h3><p>{ru?"Учебные данные привязаны к ученику и проектируются с возможностью удаления.":"Your learning data is student-scoped and designed for deletion-ready workflows."}</p></div><button className={styles.secondaryButton}>{ru?"Проверить":"Review"}</button></article>
      <article><div><h3>{ru?"Выйти":"Sign out"}</h3><p>{ru?"Завершить текущую учебную сессию на этом устройстве.":"End the current learning session on this device."}</p></div><button className={styles.secondaryButton}>{ru?"Выйти":"Sign out"}</button></article>
    </div>
  </>;
}
