import sqlite3, os, time
import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    wamid TEXT PRIMARY KEY,  -- idempotency: prevents duplicate replies
    wa_id TEXT NOT NULL,
    direction TEXT,
    type TEXT,
    content_redacted TEXT,
    intent TEXT,
    status TEXT,
    created_at INTEGER,
    retention_until INTEGER
);
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wamid TEXT NOT NULL,
    wa_id TEXT,
    job_type TEXT,
    payload_json TEXT,
    status TEXT DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS contacts (
    wa_id TEXT PRIMARY KEY,
    last_seen_at INTEGER
);
CREATE TABLE IF NOT EXISTS suppressions (
    wa_id TEXT PRIMARY KEY,
    reason TEXT,
    created_at INTEGER
);
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wamid TEXT,
    action TEXT,
    created_at INTEGER
);
"""

def get_conn():
    os.makedirs(os.path.dirname(config.DATABASE_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

def is_duplicate(conn, wamid):
    return conn.execute("SELECT 1 FROM messages WHERE wamid=?", (wamid,)).fetchone() is not None
