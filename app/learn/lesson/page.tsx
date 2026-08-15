"use client";

import Link from "next/link";
import { useState } from "react";
import styles from "../learn.module.css";

export default function LessonPage(){
  const [answer,setAnswer]=useState("");
  const [quizResult,setQuizResult]=useState("");
  const [speaking,setSpeaking]=useState(false);
  const [completed,setCompleted]=useState(false);

  function checkAnswer(value:string){
    setAnswer(value);
    setQuizResult(value === "What about you?" ? "Correct — this invites the other person to continue the conversation." : "Almost. Choose the phrase that asks the other person to respond.");
  }

  function completeLesson(){
    setCompleted(true);
    if(typeof window!=="undefined"){
      localStorage.setItem("aira.lesson.english.a1.1","completed");
      localStorage.setItem("aira.lesson.lastCompleted",new Date().toISOString());
    }
  }

  return <div>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>ENGLISH • A1 • LESSON 1</span><h1>Introduce yourself confidently</h1><p>Learn the phrases, practise them aloud, then complete a short real-life task with AIRA.</p></div>
    <div className={styles.lessonLayout}>
      <main className={styles.lessonContent}>
        <section className={styles.videoCard}><div className={styles.videoStage}><div className={styles.playButton}>▶</div><span>AIRA VIDEO LESSON</span></div><div className={styles.videoMeta}><strong>01. Meeting someone for the first time</strong><span>8 min</span></div></section>
        <section className={styles.panel}><span className={styles.eyebrow}>TODAY'S GOAL</span><h2>Say who you are without translating every word</h2><p>By the end of this lesson you can greet someone, say your name, where you are from and what you do, then ask the same questions back.</p><div className={styles.phraseGrid}><article><small>Greeting</small><strong>Hi, nice to meet you.</strong><span>Привет, приятно познакомиться.</span></article><article><small>About you</small><strong>I'm Kristina. I'm from Lithuania.</strong><span>Я Кристина. Я из Литвы.</span></article><article><small>Keep talking</small><strong>What about you?</strong><span>А ты?</span></article></div></section>
        <section className={styles.panel}><span className={styles.eyebrow}>PRACTICE</span><h2>Build your introduction</h2><div className={styles.practiceBox}><p>Complete this pattern aloud:</p><blockquote>Hi! I'm ____. I'm from ____. I work / study ____. Nice to meet you. What about you?</blockquote><button onClick={()=>setSpeaking(!speaking)} className={styles.primaryButton}>{speaking ? "✓ Speaking practice started" : "🎙 Start speaking practice"}</button>{speaking && <p>Say the introduction aloud twice. First slowly, then once at natural speed. Voice recording will be connected in the Voice Tutor sprint.</p>}</div></section>
        <section className={styles.quizCard}><div><span className={styles.eyebrow}>QUICK CHECK</span><h2>Which phrase keeps the conversation going?</h2></div><div className={styles.answerGrid}>{["I'm from Lithuania.","What about you?","Nice to meet you."].map(option=><button key={option} onClick={()=>checkAnswer(option)} aria-pressed={answer===option}>{option}</button>)}</div>{quizResult && <p><strong>{answer === "What about you?" ? "✓ Correct" : "Try again"}</strong> — {quizResult}</p>}</section>
        {completed && <section className={styles.panel}><span className={styles.eyebrow}>LESSON COMPLETE</span><h2>Great work — Lesson 1 is complete.</h2><p>Your completion has been saved on this device. Next we will connect this event to the learner account and Academy progress history.</p><Link href="/learn/practice" className={styles.primaryButton}>Continue to conversation practice →</Link></section>}
        <div className={styles.lessonFooter}><Link href="/learn/courses" className={styles.secondaryButton}>← Course</Link><button onClick={completeLesson} disabled={answer!=="What about you?"} className={styles.primaryButton}>{completed ? "✓ Lesson completed" : "Complete lesson →"}</button></div>
      </main>
      <aside className={styles.tutorPanel}><div className={styles.tutorHeader}><div className={styles.aiOrb}>A</div><div><strong>AIRA Tutor</strong><span>Online • lesson-aware</span></div></div><div className={styles.chat}><div className={styles.aiMessage}>Hi! I'm here with you during this lesson. Ask me to explain a phrase, correct your sentence or practise a dialogue.</div><div className={styles.quickPrompts}><Link href="/learn/tutor">Explain simply</Link><Link href="/learn/tutor">Check my sentence</Link><Link href="/learn/practice">Practise dialogue</Link><Link href="/learn/tutor">Give me 3 examples</Link></div></div><div className={styles.chatInput}><input placeholder="Ask AIRA about this lesson…"/><Link href="/learn/tutor">↑</Link></div><p className={styles.tutorNote}>AIRA adapts explanations to your level and keeps the conversation focused on the current lesson.</p></aside>
    </div>
  </div>
}
