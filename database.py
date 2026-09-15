
import sqlite3, time, os

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    wamid TEXT PRIMARY KEY,
    wa_id TEXT NOT NULL,
    content_redacted TEXT,
    intent TEXT,
    action TEXT,
    priority TEXT,
    status TEXT,
    created_at INTEGER,
    retention_until INTEGER
);
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wamid TEXT NOT NULL,
    wa_id TEXT,
    intent TEXT,
    priority TEXT,
    status TEXT DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS contacts (
    wa_id TEXT PRIMARY KEY,
    last_seen INTEGER,
    last_intent TEXT
);
CREATE TABLE IF NOT EXISTS suppressions (
    wa_id TEXT PRIMARY KEY,
    reason TEXT,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wamid TEXT,
    wa_id TEXT,
    action TEXT,
    intent TEXT,
    created_at INTEGER
);
"""

def get_db_path():
    return os.getenv("DATABASE_PATH", "/tmp/medsforless_phase1_v1_1.db")

def get_conn():
    conn = sqlite3.connect(get_db_path(), timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

def insert_message(wamid, wa_id, content_redacted, intent, action, priority, status="received"):
    conn = get_conn()
    now = int(time.time())
    retention = now + 7*24*3600  # 7 days per security review
    try:
        conn.execute("INSERT INTO messages (wamid, wa_id, content_redacted, intent, action, priority, status, created_at, retention_until) VALUES (?,?,?,?,?,?,?,?,?)",
                     (wamid, wa_id, content_redacted, intent, action, priority, status, now, retention))
        conn.execute("INSERT INTO jobs (wamid, wa_id, intent, priority, status, created_at) VALUES (?,?,?,?,?,?)",
                     (wamid, wa_id, intent, priority, "pending", now))
        conn.execute("INSERT OR REPLACE INTO contacts (wa_id, last_seen, last_intent) VALUES (?,?,?)",
                     (wa_id, now, intent))
        conn.execute("INSERT INTO audit_logs (wamid, wa_id, action, intent, created_at) VALUES (?,?,?,?,?)",
                     (wamid, wa_id, action, intent, now))
        if intent == "opt_out":
            conn.execute("INSERT OR REPLACE INTO suppressions (wa_id, reason, created_at) VALUES (?,?,?)",
                         (wa_id, "STOP", now))
        conn.commit()
        msg = f"INSERTED wamid PK={wamid}"
        ok = True
    except sqlite3.IntegrityError as e:
        # wamid PRIMARY KEY — no duplicate replies — exit criteria
        msg = f"DUPLICATE BLOCKED (idempotency): {e}"
        ok = False
    except Exception as e:
        msg = f"ERROR: {e}"
        ok = False
    finally:
        conn.close()
    return ok, msg

def get_stats():
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        jobs_pending = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='pending'").fetchone()[0]
        jobs_done = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='done'").fetchone()[0]
        supp = conn.execute("SELECT COUNT(*) FROM suppressions").fetchone()[0]
        urgent = conn.execute("SELECT COUNT(*) FROM jobs WHERE priority='URGENT' AND status='pending'").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM jobs WHERE priority='HIGH' AND status='pending'").fetchone()[0]
        normal = conn.execute("SELECT COUNT(*) FROM jobs WHERE priority='NORMAL' AND status='pending'").fetchone()[0]
        return {"total": total, "pending": jobs_pending, "done": jobs_done, "supp": supp, "urgent": urgent, "high": high, "normal": normal}
    finally:
        conn.close()

def get_recent(limit=20):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT wa_id, intent, action, priority, content_redacted, created_at FROM messages ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_pending_by_priority(priority, limit=20):
    conn = get_conn()
    try:
        rows = conn.execute("SELECT wamid, wa_id, intent, priority, status, created_at FROM jobs WHERE priority=? AND status='pending' ORDER BY created_at ASC LIMIT ?", (priority, limit)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def mark_job_done(wamid):
    conn = get_conn()
    try:
        conn.execute("UPDATE jobs SET status='done' WHERE wamid=?", (wamid,))
        conn.execute("UPDATE messages SET status='processed' WHERE wamid=?", (wamid,))
        conn.commit()
    finally:
        conn.close()
