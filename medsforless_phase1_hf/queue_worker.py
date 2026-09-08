import threading, queue, json, time, logging
import config
from database import get_conn
from intents import RESPONSES
from whatsapp_client import WhatsAppClient
from security import safe_log

logger = logging.getLogger("worker")
job_queue = queue.Queue()
wa_client = WhatsAppClient()

def worker_loop():
    while True:
        try:
            job = job_queue.get(timeout=5)
            process_job(job)
            job_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.exception(f"Worker error: {e}")

def process_job(job):
    wamid = job["wamid"]
    wa_id = job["wa_id"]
    payload = json.loads(job["payload_json"])
    intent = payload.get("intent", "general")

    conn = get_conn()
    try:
        # Check suppression - Phase 1 opt-out
        if conn.execute("SELECT 1 FROM suppressions WHERE wa_id=?", (wa_id,)).fetchone():
            conn.execute("UPDATE jobs SET status='suppressed' WHERE wamid=?", (wamid,))
            conn.commit()
            conn.close()
            return

        reply = RESPONSES.get(intent, RESPONSES["general"])
        wa_client.send_text(wa_id, reply)

        conn.execute("UPDATE messages SET status='processed' WHERE wamid=?", (wamid,))
        conn.execute("UPDATE jobs SET status='done', attempts=attempts+1 WHERE wamid=?", (wamid,))
        conn.execute("INSERT INTO audit_logs (wamid, action, created_at) VALUES (?,?,?)", (wamid, f"reply:{intent}", int(time.time())))
        conn.commit()
        logger.info(f"Processed {safe_log(wamid)} intent={intent}")
    except Exception as e:
        conn.execute("UPDATE jobs SET status='failed', last_error=? WHERE wamid=?", (str(e)[:500], wamid))
        conn.commit()
    finally:
        conn.close()

def start_workers(n=None):
    n = n or config.WORKER_COUNT
    for i in range(n):
        threading.Thread(target=worker_loop, daemon=True).start()
    logger.info(f"Started {n} workers - Phase 1 queue")
