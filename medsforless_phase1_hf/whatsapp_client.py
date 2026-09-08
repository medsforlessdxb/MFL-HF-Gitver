import requests, logging
import config
from security import safe_log
logger = logging.getLogger("wa_client")

class WhatsAppClient:
    def __init__(self):
        self.token = config.WHATSAPP_TOKEN
        self.phone_id = config.PHONE_NUMBER_ID
        self.version = config.GRAPH_API_VERSION
        self.base = f"https://graph.facebook.com/{self.version}/{self.phone_id}/messages"
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def send_text(self, to_wa_id, text):
        # Phase 1: resilient outbound with timeouts per High fix
        if not self.token:
            logger.info(f"MOCK send to {safe_log(to_wa_id)}: {safe_log(text)}")
            return {"mocked": True}

        payload = {
            "messaging_product": "whatsapp",
            "to": to_wa_id,
            "type": "text",
            "text": {"body": text[:1000]}
        }
        for attempt in range(3):
            try:
                r = self.session.post(self.base, json=payload, timeout=(3.05, 10))
                if r.status_code >= 400:
                    logger.error(f"Graph API {r.status_code}: {safe_log(r.text)}")
                    if r.status_code in [429,500,502,503] and attempt < 2:
                        continue
                    return {"error": r.text}
                return r.json()
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout attempt {attempt+1}")
                if attempt == 2:
                    raise
