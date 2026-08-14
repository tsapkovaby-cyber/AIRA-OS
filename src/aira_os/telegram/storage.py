from __future__ import annotations

import json
import sqlite3
from threading import Lock
from .models import ActionProposal, ConversationMode, ConversationSession, now


class Store:
    """Durable sessions, idempotency, queue, bounded history, and proposals."""
    def __init__(self, path: str):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.lock = Lock()
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS updates(update_id INTEGER PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL, error TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(chat_id INTEGER NOT NULL, user_id INTEGER NOT NULL, session_id TEXT UNIQUE NOT NULL, mode TEXT NOT NULL, memory_context TEXT NOT NULL, created_at TEXT NOT NULL, last_active TEXT NOT NULL, status TEXT NOT NULL, PRIMARY KEY(chat_id,user_id));
        CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS proposals(proposal_id TEXT PRIMARY KEY, action TEXT NOT NULL, reason TEXT NOT NULL, risk TEXT NOT NULL, cost REAL NOT NULL, preview TEXT NOT NULL, requested_by INTEGER NOT NULL, created_at TEXT NOT NULL, status TEXT NOT NULL, expires_at TEXT);
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        """)
        self.db.commit()

    def enqueue_once(self, update_id: int, payload: dict) -> bool:
        with self.lock:
            try:
                self.db.execute("INSERT INTO updates VALUES(?,?,?,?,?)", (update_id, json.dumps(payload), "QUEUED", None, now()))
                self.db.commit(); return True
            except sqlite3.IntegrityError:
                return False

    def next_update(self):
        with self.lock:
            row = self.db.execute("SELECT * FROM updates WHERE status='QUEUED' ORDER BY update_id LIMIT 1").fetchone()
            if row:
                self.db.execute("UPDATE updates SET status='PROCESSING' WHERE update_id=?", (row["update_id"],)); self.db.commit()
            return row

    def finish(self, update_id: int, error: str | None = None):
        self.db.execute("UPDATE updates SET status=?,error=? WHERE update_id=?", ("FAILED" if error else "COMPLETED", error, update_id)); self.db.commit()

    def session(self, chat_id: int, user_id: int) -> ConversationSession:
        row = self.db.execute("SELECT * FROM sessions WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
        if row:
            self.db.execute("UPDATE sessions SET last_active=? WHERE session_id=?", (now(), row["session_id"])); self.db.commit()
            return ConversationSession(chat_id, user_id, row["session_id"], conversation_mode=ConversationMode(row["mode"]), memory_context=json.loads(row["memory_context"]), created_at=row["created_at"], last_active=now(), status=row["status"])
        item = ConversationSession(chat_id, user_id)
        self.db.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?)", (chat_id,user_id,item.session_id,item.conversation_mode,json.dumps({}),item.created_at,item.last_active,item.status)); self.db.commit()
        return item

    def add_history(self, session_id: str, role: str, content: str):
        self.db.execute("INSERT INTO history(session_id,role,content,created_at) VALUES(?,?,?,?)", (session_id,role,content,now()))
        self.db.execute("DELETE FROM history WHERE session_id=? AND id NOT IN (SELECT id FROM history WHERE session_id=? ORDER BY id DESC LIMIT 40)", (session_id,session_id)); self.db.commit()

    def history(self, session_id: str, limit: int = 20) -> list[dict]:
        rows = self.db.execute("SELECT role,content FROM history WHERE session_id=? ORDER BY id DESC LIMIT ?", (session_id,limit)).fetchall()
        return [dict(row) for row in reversed(rows)]

    def save_proposal(self, p: ActionProposal):
        self.db.execute("INSERT INTO proposals VALUES(?,?,?,?,?,?,?,?,?,?)", (p.proposal_id,p.action,p.reason,p.risk,p.cost,p.preview,p.requested_by,p.created_at,p.approval_status,p.expires_at)); self.db.commit()

    def proposal(self, proposal_id: str):
        return self.db.execute("SELECT * FROM proposals WHERE proposal_id=?", (proposal_id,)).fetchone()

    def decide(self, proposal_id: str, user_id: int, decision: str) -> bool:
        with self.lock:
            cur = self.db.execute("UPDATE proposals SET status=? WHERE proposal_id=? AND requested_by=? AND status='PENDING'", (decision,proposal_id,user_id)); self.db.commit(); return cur.rowcount == 1

    def pending(self, user_id: int):
        return self.db.execute("SELECT * FROM proposals WHERE requested_by=? AND status='PENDING' ORDER BY created_at", (user_id,)).fetchall()

    def set_paused(self, value: bool):
        self.db.execute("INSERT OR REPLACE INTO settings VALUES('pause_autonomy',?)", ("true" if value else "false",)); self.db.commit()

    def paused(self) -> bool:
        row = self.db.execute("SELECT value FROM settings WHERE key='pause_autonomy'").fetchone()
        return bool(row and row[0] == "true")
