"""
WhatsApp Graph API sender for Medsforless Phase 1 v1.1
Sends text replies via Meta Cloud API
"""
import httpx
import logging
from app import config
from app.security import safe_log

logger = logging.getLogger(__name__)

def send_text(wa_id: str, text: str) -> dict:
    """Send a WhatsApp text message via Graph API.
    If WHATSAPP_TOKEN or PHONE_NUMBER_ID is empty, runs in mock mode (logs only).
    """
    if not config.WHATSAPP_TOKEN or not config.PHONE_NUMBER_ID:
        logger.info(f"MOCK send to {safe_log(wa_id)}: {safe_log(text)}")
        return {"mocked": True}

    url = f"https://graph.facebook.com/{config.GRAPH_API_VERSION}/{config.PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "text",
        "text": {"body": text}
    }

    try:
        with httpx.Client(timeout=10) as client:
            r = client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                logger.info(f"Sent to {safe_log(wa_id)}: {safe_log(text[:50])}")
            else:
                logger.error(f"Graph API {r.status_code}: {r.text[:200]}")
            return r.json()
    except Exception as e:
        logger.error(f"Send failed to {safe_log(wa_id)}: {e}")
        return {"error": str(e)}
