
import sys
sys.path.insert(0, ".")
from app.database import init_db, get_conn, insert_message
from app.classifier import classify
from app.security import safe_log

def test_idempotency():
    print("Test 1: Idempotency wamid PRIMARY KEY")
    init_db()
    conn = get_conn()
    wid = "wamid.test.replay.123"
    conn.execute("DELETE FROM messages WHERE wamid=?", (wid,))
    conn.commit()
    ok1, msg1 = insert_message(wid, "9715", "test", "faq_greeting", "auto_reply", "LOW")
    ok2, msg2 = insert_message(wid, "9715", "test", "faq_greeting", "auto_reply", "LOW")
    conn.close()
    assert ok1 == True, "First insert should succeed"
    assert ok2 == False, "Second insert should be blocked by PK"
    assert "DUPLICATE BLOCKED" in msg2 or "UNIQUE" in msg2 or "BLOCKED" in msg2
    print("✅ PASS - No duplicate replies")

def test_redacted_logs():
    print("\nTest 2: Redacted logs safe_log")
    redacted = safe_log("My number 971506583391 and email test@example.com")
    assert "[REDACTED_WA_ID]" in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "971506583391" not in redacted
    print(f"✅ PASS - Redacted: {redacted}")

def test_qa_classifier():
    print("\nTest 3: QA v1.1 classifier 22 intents")
    cases = [
        ("Hi", False, "text", "faq_greeting"),
        ("How does this work?", False, "text", "service_explanation"),
        ("I need tramadol", False, "text", "controlled_substance_block"),
        ("", True, "image", "prescription_image"),
        ("STOP", False, "text", "opt_out"),
        ("What is dosage?", False, "text", "clinical_question"),
    ]
    for text, has_media, mtype, expected in cases:
        intent, action, prio, conf, ext = classify(text, has_media, mtype)
        assert intent == expected, f"Expected {expected} got {intent} for '{text}'"
    print("✅ PASS - QA classifier works")

if __name__ == "__main__":
    test_idempotency()
    test_redacted_logs()
    test_qa_classifier()
    print("\nAll exit criteria PASS - Phase 1 ready")
