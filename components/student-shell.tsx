import Link from "next/link";
import styles from "../app/learn/learn.module.css";

const nav = [
  ["/learn", "Dashboard"],
  ["/learn/courses", "My Learning"],
  ["/learn/catalog", "Courses"],
  ["/learn/progress", "Progress"],
  ["/learn/tutor", "AI Tutor"],
  ["/learn/profile", "Profile"],
  ["/learn/settings", "Settings"],
] as const;

export function StudentShell({ children }: { children: React.ReactNode }) {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <Link className={styles.brand} href="/learn"><span className={styles.brandMark}>A</span><span>AIRA <small>Academy</small></span></Link>
        <nav className={styles.nav} aria-label="Student navigation">
          {nav.map(([href, label]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
        <div className={styles.sidebarCard}><strong>Daily goal</strong><span>20 min</span><div className={styles.miniBar}><i /></div><small>Keep your streak alive</small></div>
      </aside>
      <div className={styles.main}><header className={styles.topbar}><div><span className={styles.eyebrow}>AIRA LEARNING PLATFORM</span></div><div className={styles.topActions}><button aria-label="Notifications">◌</button><div className={styles.avatar}>K</div></div></header><main className={styles.content}>{children}</main></div>
    </div>
  );
}
