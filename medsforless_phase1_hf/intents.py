"""
Phase 1 ONLY - Deterministic MVP per doc:
- No LLM
- No dosage extraction
- No media processing (Phase 3)
- Only: FAQ auto-reply, office hours, human handoff for medicine/clinical/prescription
"""
from datetime import datetime
import pytz
import config

def is_office_hours():
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz)
    return config.OFFICE_START_HOUR <= now.hour < config.OFFICE_END_HOUR

def classify_phase1(text: str, has_media: bool = False):
    """
    Returns: intent, action
    Phase 1 allowed auto: faq_greeting, office_hours
    Everything else: escalate to human
    """
    t = (text or "").lower().strip()

    # Opt-out - Phase 1 must have suppression
    if any(k in t for k in ["stop", "unsubscribe"]):
        return "opt_out", "suppression"

    # Phase 3 not in Phase 1: if media sent, escalate + tell not supported yet
    if has_media:
        return "prescription_image", "escalate_human_phase3_not_in_phase1"

    # Blocked medical intents -> always human per Critical fix
    if any(k in t for k in ["dosage", "dose", "side effect", "interaction", "substitute", "how much should"]):
        return "clinical_question", "escalate_human_safety"

    if any(k in t for k in ["price", "panadol", "buy", "need medicine", "order", "available"]):
        return "medicine_request", "escalate_human"

    # FAQ - allowed auto in Phase 1
    if any(k in t for k in ["hi", "hello", "salam", "hours", "open", "location"]):
        if not is_office_hours():
            return "office_hours", "auto_reply_office_hours"
        return "faq_greeting", "auto_reply"

    return "general", "escalate_human"

RESPONSES = {
    "faq_greeting": "Hello from Medsforless! We are open 9AM-11PM Dubai. Share your medicine name and our pharmacist will confirm. (Phase 1 - deterministic, no LLM)",
    "office_hours": "We are currently closed (9AM-11PM Dubai). Your message is queued and pharmacist will reply during office hours. (Phase 1 - office hours check)",
    "clinical_question": "For safety, dosage/side-effect questions are answered ONLY by licensed pharmacist (per safety review). Escalated to human. (Phase 1 - no auto clinical)",
    "medicine_request": "Medicine request received. Escalated to human pharmacist for price & availability (Phase 1 - human handoff).",
    "prescription_image": "Received image - Note: Media intake is Phase 3, not Phase 1. Escalated to human for manual review. No auto dosage extraction per Critical fix.",
    "opt_out": "You are unsubscribed. Reply START to resubscribe. (Phase 1 - suppression table)",
    "general": "Thanks for messaging Medsforless. Our team will review (Phase 1 - human handoff)."
}
