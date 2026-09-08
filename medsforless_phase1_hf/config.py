import os
from dotenv import load_dotenv
load_dotenv()

META_APP_SECRET = os.getenv("META_APP_SECRET", "")  # Critical: for X-Hub-Signature-256
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "medsforless_verify_2026")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")  # leave empty for HF demo = mocked
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
DATABASE_PATH = os.getenv("DATABASE_PATH", "/tmp/medsforless_phase1.db")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")  # not hard-coded v18.0

# Phase 1 only: office hours (Dubai)
OFFICE_START_HOUR = 9
OFFICE_END_HOUR = 23
TIMEZONE = "Asia/Dubai"

WORKER_COUNT = 2
RETENTION_DAYS = 7  # Phase 1 minimal retention
