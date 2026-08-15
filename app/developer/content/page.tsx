"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type Status = "Draft" | "Review" | "Published";
type ContentItem = { id:string; type:string; title:string; language:string; level:string; status:Status };

const defaults:ContentItem[]=[
  {id:"en-a1-lesson-1",type:"Урок",title:"Первое знакомство",language:"English",level:"A1",status:"Published"},
  {id:"en-a1-practice-1",type:"Практика",title:"Представься собеседнику",language:"English",level:"A1",status:"Review"},
  {id:"ru-a1-course",type:"Курс",title:"Русский для общения",language:"Русский",level:"A1",status:"Draft"},
];

export default function ContentStudio(){
  const [items,setItems]=useState<ContentItem[]>(defaults);
  const [saved,setSaved]=useState(false);
  useEffect(()=>{try{const raw=localStorage.getItem("aira.founder.content");if(raw)setItems(JSON.parse(raw));}catch{}},[]);
  function setStatus(id:string,status:Status){setItems(current=>current.map(item=>item.id===id?{...item,status}:item));setSaved(false);}
  function save(){localStorage.setItem("aira.founder.content",JSON.stringify(items));setSaved(true);}
  return <main>
    <div className="page-head"><div><p className="eyebrow">FOUNDER · CONTENT STUDIO</p><h1>Контент и учебная программа</h1><p className="muted">Рабочая зона статусов контента, проверки уроков и подготовки будущего серверного CRUD.</p></div><Link className="button" href="/developer">← Кабинет основателя</Link></div>
    <div className="grid"><article className="card metric"><span className="eyebrow">ЯЗЫКИ</span><div className="value">10</div><span className="muted">Активный каталог Academy</span></article><article className="card metric"><span className="eyebrow">DRAFT</span><div className="value">{items.filter(i=>i.status==="Draft").length}</div><span className="muted">Требуют доработки</span></article><article className="card metric"><span className="eyebrow">REVIEW</span><div className="value">{items.filter(i=>i.status==="Review").length}</div><span className="muted">Ожидают проверки</span></article><article className="card metric"><span className="eyebrow">PUBLISHED</span><div className="value">{items.filter(i=>i.status==="Published").length}</div><span className="muted">Готово для учеников</span></article></div>
    <section className="card" style={{marginTop:20}}><div className="section-head"><h2>Редактор статусов</h2><button className="button primary" onClick={save}>{saved?"✓ Сохранено":"Сохранить изменения"}</button></div><div className="table-wrap"><table><thead><tr><th>Тип</th><th>Название</th><th>Язык</th><th>Уровень</th><th>Статус</th><th>Проверка</th></tr></thead><tbody>{items.map(item=><tr key={item.id}><td>{item.type}</td><td>{item.title}</td><td>{item.language}</td><td>{item.level}</td><td><select value={item.status} onChange={e=>setStatus(item.id,e.target.value as Status)}><option>Draft</option><option>Review</option><option>Published</option></select></td><td><Link href={item.type==="Практика"?"/learn/practice":item.type==="Урок"?"/learn/lesson":"/learn/catalog"}>Открыть →</Link></td></tr>)}</tbody></table></div><p className="muted">Сейчас статусы сохраняются локально в founder-сессии браузера. После подключения database этот же интерфейс будет писать в серверный content registry.</p></section>
    <div className="controls" style={{marginTop:20}}><Link className="button" href="/learn/catalog">Каталог языков</Link><Link className="button" href="/learn/lesson">Проверить урок</Link><Link className="button" href="/learn/practice">Проверить практику</Link><Link className="button" href="/developer/settings">Настройки Academy</Link></div>
  </main>;
}
