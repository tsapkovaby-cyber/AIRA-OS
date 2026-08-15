export type UiLanguage = "ru" | "en";

const KEY = "aira.uiLanguage";

export function getUiLanguage(): UiLanguage {
  if (typeof window === "undefined") return "ru";
  const value = window.localStorage.getItem(KEY);
  return value === "en" ? "en" : "ru";
}

export function setUiLanguage(language: UiLanguage) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(KEY, language);
  document.documentElement.lang = language;
  window.dispatchEvent(new CustomEvent("aira:language", { detail: language }));
}
