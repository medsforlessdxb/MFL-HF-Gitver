import hmac, hashlib, re

def verify_meta_signature(raw_body: bytes, sig_header: str, secret: str) -> bool:
    """Phase 1 Critical: Verify X-Hub-Signature-256 BEFORE parsing JSON"""
    if not secret:
        return True  # dev only
    if not sig_header or not sig_header.startswith("sha256="):
        return False
    sig = sig_header.split("sha256=")[1]
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)

def safe_log(text: str) -> str:
    """Phase 1: Verified logs - redact PII per doc"""
    if not text:
        return ""
    t = str(text)[:150]
    # redact wa_id
    t = re.sub(r"971\d{7,12}", "[REDACTED_WA_ID]", t)
    return t
