"use client";

import { useState } from "react";
import styles from "../learn.module.css";

const scenarios = [
  { id: "cafe", title: "Order at a café", level: "A1", prompt: "Good morning! What would you like to order?" },
  { id: "meeting", title: "Meet someone new", level: "A1-A2", prompt: "Hi! Nice to meet you. What's your name?" },
  { id: "travel", title: "Airport check-in", level: "A2", prompt: "Good afternoon. May I see your passport and ticket, please?" },
];

export default function PracticePage() {
  const [scenario, setScenario] = useState(scenarios[0]);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");

  function reviewAnswer() {
    const text = answer.trim();
    if (!text) return setFeedback("Write your answer first. AIRA will help you improve it.");
    if (text.length < 12) return setFeedback("Good start. Try a complete sentence and add one polite phrase.");
    setFeedback("Your meaning is clear. Now repeat it naturally without translating word by word.");
  }

  return <div>
    <div className={styles.pageHeading}><span className={styles.eyebrow}>CONVERSATIONAL PRACTICE</span><h1>Speak with AIRA</h1><p>Choose a real-life situation, respond in English and receive level-appropriate coaching.</p></div>
    <div className={styles.practiceLayout}>
      <aside className={styles.scenarioList}><span className={styles.eyebrow}>SCENARIOS</span>{scenarios.map(item => <button key={item.id} onClick={() => { setScenario(item); setAnswer(""); setFeedback(""); }} className={item.id === scenario.id ? styles.scenarioActive : ""}><strong>{item.title}</strong><span>{item.level}</span></button>)}</aside>
      <main className={styles.conversationCard}>
        <div className={styles.conversationHeader}><div><span className={styles.pill}>{scenario.level}</span><h2>{scenario.title}</h2><p>Complete five exchanges. Focus on communicating clearly before perfect grammar.</p></div><div className={styles.aiOrb}>A</div></div>
        <div className={styles.dialogueArea}><div className={styles.aiMessage}>I'll play the other person. Mistakes are welcome — I'll correct only what helps you communicate better.</div><div className={styles.aiMessage}>{scenario.prompt}</div>{answer && <div className={styles.studentMessage}>{answer}</div>}{feedback && <div className={styles.feedbackCard}><strong>AIRA feedback</strong><span>{feedback}</span><small>Tip: confidence first, accuracy through repetition.</small></div>}</div>
        <div className={styles.responseComposer}><textarea value={answer} onChange={event => setAnswer(event.target.value)} placeholder="Type what you would say..."/><div><button className={styles.secondaryButton}>🎙 Speak</button><button onClick={reviewAnswer} className={styles.primaryButton}>Send to AIRA →</button></div></div>
      </main>
      <aside className={styles.coachCard}><span className={styles.eyebrow}>YOUR COACH</span><h3>Practice settings</h3><label>Difficulty<select defaultValue="guided"><option>Guided</option><option>Natural</option><option>Challenge me</option></select></label><div className={styles.coachStat}><span>Goal</span><strong>5 exchanges</strong></div><div className={styles.coachStat}><span>Focus</span><strong>Confidence</strong></div><p>Learning Memory will later turn repeated mistakes into personalized exercises.</p></aside>
    </div>
  </div>;
}
