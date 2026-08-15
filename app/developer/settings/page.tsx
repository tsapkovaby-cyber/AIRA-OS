"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Settings={defaultUiLanguage:"ru"|"en";tutorEnabled:boolean;voiceEnabled:boolean;practiceEnabled:boolean;experimental:boolean;dailyMinutes:number;maintenance:boolean};
const defaults:Settings={defaultUiLanguage:"ru",tutorEnabled:true,voiceEnabled:false,practiceEnabled:true,experimental:false,dailyMinutes:20,maintenance:false};

export default function FounderSettings(){
  const [settings,setSettings]=useState<Settings>(defaults); const [saved,setSaved]=useState(false);
  useEffect(()=>{try{const raw=localStorage.getItem("aira.founder.settings");if(raw)setSettings({...defaults,...JSON.parse(raw)});}catch{}},[]);
  function save(){localStorage.setItem("aira.founder.settings",JSON.stringify(settings));setSaved(true);}
  const toggle=(key:keyof Settings)=>(event:React.ChangeEvent<HTMLInputElement>)=>{setSettings(current=>({...current,[key]:event.target.type==="checkbox"?event.target.checked:Number(event.target.value)}));setSaved(false);};
  return <main><div className="page-head"><div><p className="eyebrow">FOUNDER · ACADEMY SETTINGS</p><h1>Глобальные настройки платформы</h1><p className="muted">Отдельные owner-настройки функций Academy. Они не смешиваются с личными настройками ученика.</p></div><Link className="button" href="/developer">← Кабинет основателя</Link></div>
  <div className="two-col"><section className="card"><h2>Язык и обучение</h2><label className="field"><span>Язык интерфейса по умолчанию</span><select value={settings.defaultUiLanguage} onChange={e=>{setSettings({...settings,defaultUiLanguage:e.target.value as "ru"|"en"});setSaved(false);}}><option value="ru">Русский</option><option value="en">English</option></select></label><label className="field"><span>Дневная цель, минут</span><input type="number" min={5} max={180} value={settings.dailyMinutes} onChange={toggle("dailyMinutes")}/></label><p className="muted">Персональный язык ученика по-прежнему можно менять в его собственных настройках.</p></section>
  <section className="card"><h2>AI-функции</h2><label><input type="checkbox" checked={settings.tutorEnabled} onChange={toggle("tutorEnabled")}/> AIRA Tutor</label><br/><label><input type="checkbox" checked={settings.voiceEnabled} onChange={toggle("voiceEnabled")}/> Voice Tutor</label><br/><label><input type="checkbox" checked={settings.practiceEnabled} onChange={toggle("practiceEnabled")}/> Разговорная практика</label><br/><label><input type="checkbox" checked={settings.experimental} onChange={toggle("experimental")}/> Экспериментальные функции</label></section></div>
  <section className="card" style={{marginTop:20}}><h2>Операционные режимы</h2><label><input type="checkbox" checked={settings.maintenance} onChange={toggle("maintenance")}/> Maintenance mode</label><p className="muted">Сейчас переключатели сохраняются в founder-конфигурации браузера и используются как безопасный UI-прототип. Перед влиянием на production-функции их подключим к server-side config с audit log.</p></section>
  <div className="controls" style={{marginTop:20}}><button className="button primary" onClick={save}>{saved?"✓ Настройки сохранены":"Сохранить настройки"}</button><Link className="button" href="/learn/settings">Настройки ученика</Link><Link className="button" href="/developer/tutor">Tutor & Voice</Link><Link className="button" href="/developer/security">Security & Audit</Link></div></main>;
}
