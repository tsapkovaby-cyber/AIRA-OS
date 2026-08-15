"use client";

import { useEffect, useState } from "react";
import { getUiLanguage, type UiLanguage } from "./ui-language";

export function useUiLanguage(){
  const [language,setLanguage]=useState<UiLanguage>("ru");
  useEffect(()=>{
    const sync=()=>setLanguage(getUiLanguage());
    sync();
    window.addEventListener("aira:language",sync);
    window.addEventListener("storage",sync);
    return ()=>{window.removeEventListener("aira:language",sync);window.removeEventListener("storage",sync);};
  },[]);
  return language;
}
