
import os
from dotenv import load_dotenv
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "medsforless_verify_2026")
APP_SECRET = os.getenv("META_APP_SECRET", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v21.0")
DATABASE_PATH = os.getenv("DATABASE_PATH", "./data/medsforless_phase1.db")
OFFICE_HOURS_START = 9
OFFICE_HOURS_END = 23
TIMEZONE = "Asia/Dubai"
RETENTION_DAYS = 7
