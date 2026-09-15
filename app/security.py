
import hmac, hashlib, re, os

def safe_log(text: str, max_len: int = 120) -> str:
    """Redact wa_id and PHI per security review Medium fix"""
    if not text:
        return ""
    t = str(text)[:max_len]
    # Redact UAE/international numbers starting 971
    t = re.sub(r"971\d{7,12}", "[REDACTED_WA_ID]", t)
    # Redact email
    t = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]", t)
    # Redact prescription-like numbers
    t = re.sub(r"\b\d{10,}\b", "[REDACTED_NUM]", t)
    return t

def verify_hmac_signature(raw_body: bytes, signature_header: str, app_secret: str) -> bool:
    """Verify X-Hub-Signature-256 BEFORE json parse — Critical fix with constant_time"""
    if not app_secret:
        return True  # dev mode, no secret set
    if not signature_header:
        return False
    try:
        # Header format: sha256=abcdef...
        if not signature_header.startswith("sha256="):
            return False
        expected_sig = signature_header.split("=",1)[1]
        computed = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
        # constant_time_compare — Critical fix
        return hmac.compare_digest(computed, expected_sig)
    except Exception:
        return False

def is_office_hours(now_utc=None):
    """Office hours 9AM-11PM Asia/Dubai per security review"""
    from datetime import datetime
    import pytz
    tz = pytz.timezone("Asia/Dubai")
    dt = datetime.now(tz) if now_utc is None else now_utc.astimezone(tz)
    return 9 <= dt.hour < 23
