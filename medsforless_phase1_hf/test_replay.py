"""
Phase 1 Exit Criteria Test: No duplicate replies; verified logs; replay tests pass
"""
import json, time
from database import get_conn, init_db
import config

def test_idempotency():
    init_db()
    conn = get_conn()
    wid = "wamid.test.replay.001"
    conn.execute("DELETE FROM messages WHERE wamid=?", (wid,))
    conn.commit()
    conn.execute("INSERT INTO messages (wamid, wa_id, content_redacted, intent, status, created_at, retention_until) VALUES (?,?,?,?,?,?,?)",
                 (wid, "971500000001", "hi", "faq_greeting", "queued", int(time.time()), int(time.time())+86400))
    conn.commit()
    try:
        conn.execute("INSERT INTO messages (wamid, wa_id, content_redacted, intent, status, created_at, retention_until) VALUES (?,?,?,?,?,?,?)",
                     (wid, "971500000001", "hi", "faq_greeting", "queued", int(time.time()), int(time.time())+86400))
        conn.commit()
        assert False, "Duplicate should have been blocked"
    except Exception as e:
        assert "UNIQUE constraint failed" in str(e) or "PRIMARY KEY" in str(e)
        print("✅ PASS - No duplicate replies: wamid PRIMARY KEY works")
    conn.close()

def test_log_redaction():
    from security import safe_log
    log = safe_log("User 971506583391 said hi")
    assert "971506583391" not in log
    assert "[REDACTED_WA_ID]" in log
    print("✅ PASS - Verified logs: wa_id redacted")

def test_deterministic_classification():
    from intents import classify_phase1
    intent, action = classify_phase1("What is dosage for amoxicillin?")
    assert intent == "clinical_question"
    assert "escalate" in action
    print("✅ PASS - Clinical -> human handoff, no auto dosage")

    intent, action = classify_phase1("What are your hours?")
    assert intent in ["faq_greeting", "office_hours"]
    print("✅ PASS - FAQ auto allowed in Phase 1")

if __name__ == "__main__":
    test_idempotency()
    test_log_redaction()
    test_deterministic_classification()
    print("\nAll Phase 1 exit criteria PASS")
