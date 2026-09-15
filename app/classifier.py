
import re, json, os
from pathlib import Path

# Load prohibited list
try:
    PROHIBITED = json.loads(Path(__file__).parent.joinpath("prohibited_meds.json").read_text())
except:
    PROHIBITED = ["testosterone","tramadol","codeine","alprazolam"]

# Try rapidfuzz, fallback to difflib
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except:
    import difflib
    HAS_RAPIDFUZZ = False
    fuzz = None

def fuzzy_match(text: str, variants: list, threshold: int = 80) -> int:
    """Return best score 0-100 for text against variants"""
    if not text:
        return 0
    t = text.lower().strip()
    best = 0
    for v in variants:
        v_low = v.lower()
        if HAS_RAPIDFUZZ:
            score = fuzz.token_set_ratio(t, v_low)
        else:
            # fallback difflib
            score = int(difflib.SequenceMatcher(None, t, v_low).ratio()*100)
        if score > best:
            best = score
    return best

# QA v1.1 variants for fuzzy matching
GREETING_VARIANTS = [
"hi","hello","hey","salam","good morning","yo","howdy","assalamu alaikum","good evening","good afternoon","hi there","hello there"
]

HOW_IT_WORKS_VARIANTS = [
"how does this work","what do you do","tell me about your service","how does it work","what you do","how do you work",
"hw does this wrk","tel me abt ur service","wat u do","explain service","how it works","process","steps"
]

TRUST_VARIANTS = [
"is this legal","is it legal","are medicines genuine","is it safe","is it genuine","are drugs real","is this legit","is it safe to order",
"are medicines safe","legal to import","is it allowed"
]

OFF_TOPIC_VARIANTS = [
"what is the weather","who are you","tell me a joke","what is your name","how is the weather","what time is it"
]

# Keywords for deterministic checks
CLINICAL_KEYWORDS = ["dosage","dose","side effect","interaction","substitute","how much should i take","can i take with","alternative","replace"]
PRICING_KEYWORDS = ["price","cost","how much","quote","pricing","rate","charges","fees"]
MEDICINE_HINTS = ["mg","tablet","capsule","strip","box","medicine","drug","prescription","need","want","buy","order","medicine name"]
STOP_KEYWORDS = ["stop","unsubscribe","opt out","opt-out","remove me","do not message","don't message"]

SINGLE_BOX_HINTS = ["single box","one box","1 box","just one","only one box"]

def contains_prohibited(text: str):
    if not text:
        return None
    t = text.lower()
    for med in PROHIBITED:
        if med.lower() in t:
            return med
    return None

def classify(text: str, has_media: bool = False, msg_type: str = "text") -> tuple:
    """
    Deterministic classifier for 22 QA scenarios v1.1
    Returns: (intent, action, priority, confidence, extracted)
    Order matters — BLOCK first per security review
    """
    txt = (text or "").lower().strip()
    raw = text or ""
    
    # 1. BLOCKLIST FIRST — Critical fix per QA 9
    prohibited_found = contains_prohibited(txt)
    if prohibited_found:
        return ("controlled_substance_block", "auto_block + escalate_audit", "HIGH", 100, {"medicine": prohibited_found})
    
    # 2. Media — Phase 3 not in Phase 1 per security review
    if has_media or msg_type in ["image","document","audio"]:
        if msg_type in ["image","document"]:
            return ("prescription_image", "escalate_human_phase3_not_in_phase1", "NORMAL", 95, {"has_media": True})
        if msg_type in ["voice","audio"]:
            return ("voice_note", "auto_fallback_unsupported_type", "LOW", 90, {"type": "voice"})
        if msg_type in ["sticker","gif"]:
            return ("sticker_gif", "auto_fallback_unsupported_type", "LOW", 90, {"type": "sticker"})
    
    # 3. STOP / Opt-out — suppression table
    for kw in STOP_KEYWORDS:
        if kw in txt:
            return ("opt_out", "auto_suppression + escalate", "HIGH", 100, {"keyword": kw})
    
    # 4. Clinical question — safety escalate
    for kw in CLINICAL_KEYWORDS:
        if kw in txt:
            return ("clinical_question", "escalate_human_safety", "URGENT", 90, {"keyword": kw})
    
    # 5. Single box warning — economic viability per Guide Step 18
    for hint in SINGLE_BOX_HINTS:
        if hint in txt:
            return ("single_box_warning", "auto_warning + escalate", "NORMAL", 85, {"hint": hint})
    
    # 6. Language — Arabic/Hindi/Urdu detection (simple script check)
    # If non-latin heavy and no English medicine name, ask for English
    non_latin = len(re.findall(r"[^\x00-\x7F]", raw))
    if non_latin > len(raw)*0.5 and len(raw) > 5:
        return ("non_english", "auto_english_request", "NORMAL", 80, {"non_latin": non_latin})
    
    # 7. Fuzzy FAQ — only for FAQ, threshold 80 per comments doc
    if fuzzy_match(txt, GREETING_VARIANTS, 80) >= 80 and len(txt) < 40 and not any(k in txt for k in MEDICINE_HINTS):
        return ("faq_greeting", "auto_reply", "LOW", fuzzy_match(txt, GREETING_VARIANTS, 80), {})
    
    if fuzzy_match(txt, HOW_IT_WORKS_VARIANTS, 80) >= 80:
        return ("service_explanation", "auto_reply", "LOW", fuzzy_match(txt, HOW_IT_WORKS_VARIANTS, 80), {})
    
    if fuzzy_match(txt, TRUST_VARIANTS, 80) >= 80:
        return ("trust_question", "auto_reply", "LOW", fuzzy_match(txt, TRUST_VARIANTS, 80), {})
    
    if fuzzy_match(txt, OFF_TOPIC_VARIANTS, 80) >= 80:
        return ("off_topic", "auto_redirect", "LOW", fuzzy_match(txt, OFF_TOPIC_VARIANTS, 80), {})
    
    # 8. Explicit intents by keywords (deterministic)
    if any(k in txt for k in ["shipping","delivery","how long","when will","courier","tracking","ship"]):
        return ("shipping_delivery", "escalate_human", "NORMAL", 85, {})
    
    if any(k in txt for k in ["payment","paid","pay","transaction","bank transfer","payment issue","paid but"]):
        return ("payment", "escalate_human_urgent", "URGENT", 85, {})
    
    if any(k in txt for k in ["customs","import","clearance","regulatory","approval","moh","dha","custom"]):
        return ("customs_import", "escalate_human", "NORMAL", 85, {})
    
    if any(k in txt for k in ["cold chain","biologic","glp","insulin","ozempic","mounjaro","refrigerat"]):
        return ("cold_chain_biologic", "escalate_human_flag_special_shipping", "HIGH", 90, {})
    
    if any(k in txt for k in ["otc","supplement","vitamin","berberine","protein","over the counter"]):
        return ("otc_supplement", "escalate_human_redirect_logic", "NORMAL", 85, {})
    
    if any(k in txt for k in ["complaint","return","damaged","wrong medicine","broken","leak","refund","complain"]):
        return ("complaint_return", "escalate_human_high_urgent", "URGENT" if "damaged" in txt or "wrong" in txt else "HIGH", 85, {})
    
    if any(k in txt for k in ["privacy","data","gdpr","my data","delete my"]):
        return ("privacy_data", "escalate_human", "NORMAL", 85, {})
    
    if any(k in txt for k in ["status","where is my order","order status","track my order","mfl-","reference"]):
        return ("order_status", "escalate_human_high", "HIGH", 85, {})
    
    if any(k in txt for k in ["reorder","refill","same order again","repeat order","same as last"]):
        return ("reorder", "escalate_human_normal", "NORMAL", 85, {})
    
    if any(k in txt for k in ["buy in india myself","i have someone in india","can you just ship","send you the medicine and you forward"]):
        return ("buy_in_india", "escalate_human_case_by_case", "NORMAL", 85, {})
    
    if any(k in txt for k in ["different from","competitor","why should i use you","instead of buying locally","amazon"]):
        return ("competitor_comparison", "auto_reply + collect", "LOW", 80, {})
    
    if any(k in txt for k in ["discount","price match","cheaper elsewhere","too high","negotiate","can you lower"]):
        return ("price_negotiation", "escalate_human", "NORMAL", 85, {})
    
    if any(k in txt for k in ["device","alternative medicine","ayurvedic","homeopathy","service fee"]):
        return ("medical_device_alt", "escalate_human", "NORMAL", 80, {})
    
    # 9. Medicine inquiry / Pricing — collect + escalate (most common)
    if any(k in txt for k in PRICING_KEYWORDS) or any(k in txt for k in MEDICINE_HINTS) or re.search(r"\b\d+\s*mg\b", txt):
        return ("medicine_inquiry", "collect + escalate_human", "NORMAL", 80, {})
    
    # 10. General fallback — escalate
    return ("general", "escalate_human", "NORMAL", 50, {})
