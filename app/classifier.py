
import re, json, os
from pathlib import Path

# Load prohibited list
try:
    PROHIBITED = json.loads(Path(__file__).parent.joinpath("prohibited_meds.json").read_text())
except:
    PROHIBITED = ["testosterone","tramadol","codeine","alprazolam","xanax","diazepam","valium","lorazepam","clonazepam","zolpidem","morphine","fentanyl","oxycodone","modafinil","ketamine","methylphenidate","nandrolone","stanozolol"]
# Always extend with brand names regardless of JSON file
BRAND_PROHIBITED = ["xanax","valium","ativan","klonopin","rivotril","ambien","provigil","ritalin","concerta","adderall","sustanon","nebido","andriol","androgel"]

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
"hi","hello","hey","salam","good morning","yo","howdy","assalamu alaikum","good evening","good afternoon","hi there","hello there","hiii","heyyy","helo","helloo","hiiii","hey there",
"namaste","namaskar","marhaba","hola","assalam o alaikum","as-salamu alaykum","salaam"
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
CLINICAL_KEYWORDS = ["dosage","dose","side effect","interaction","substitute","how much should i take","can i take","take this with","take it with",
                     "with alcohol","safe to take","stop taking","pregnan","breastfeed","alternative","replace"]
CLINICAL_EXCLUDE = re.compile(r"can i take (delivery|the delivery|the order|my order|order|the parcel|parcel|it to|them to|this to)")
PRICING_KEYWORDS = ["price","cost","how much","quote","pricing","rate","charges","fees"]
MEDICINE_HINTS = ["mg","tablet","capsule","strip","box","medicine","drug","prescription","need","want","buy","order","medicine name"]
# Opt-out: whole-message commands OR clear phrases only (never the bare word "stop" inside a sentence)
STOP_EXACT = {"stop","unsubscribe","opt out","opt-out","optout","stop all","stop messages","cancel subscription","end",
              "stop please","please stop","pls stop","plz stop","stop it","stop now","stop thanks","stop thank you","unsubscribe me"}
STOP_NEGATION = re.compile(r"(don't|dont|do not|never|not)\s+(stop|unsubscribe|opt)")
STOP_PHRASES = ["unsubscribe","opt out","opt-out","remove me from","remove my number","do not message","don't message","dont message",
                "stop messaging","stop sending","stop texting","stop contacting","no more messages"]

# Adverse reaction: strong symptoms alone, or soft symptoms + "after taking" type context
ADVERSE_STRONG = ["allergic reaction","hives","can't breathe","cant breathe","cannot breathe","difficulty breathing","trouble breathing",
                  "breathless","chest pain","unconscious","seizure","fainted","passed out","throat swelling","face swelling","swollen face","swollen lips"]
ADVERSE_SOFT = ["rash","swelling","swollen","itching","itchy","dizzy","dizziness","vomit","nausea","headache","palpitation",
                "feel sick","feeling sick","feel unwell","feeling unwell","bleeding","reaction","stomach pain","diarrhea","diarrhoea"]
ADVERSE_CONTEXT = ["i took","took the","took it","took my","i've taken","i have taken","after taking","after the medicine","after the tablet",
                   "after the injection","after the dose","after the pen","since taking","since i started","started taking","started the",
                   "gave me","made me","is causing me","caused me","now i have","now i feel"]

ACK_EXACT = {"thanks","thank you","thank u","thx","ty","ok","okay","ok thanks","okay thanks","ok thank you","great","noted","cool","fine",
             "alright","sure","got it","perfect","thanks a lot","thank you so much","shukran","jazakallah","👍","🙏","👌"}

HUMAN_PHRASES = ["talk to a human","speak to a human","talk to someone","speak to someone","real person","human agent","talk to agent",
                 "speak to agent","customer service","customer care","call me","speak to a person","talk to a person","talk to your team",
                 "can someone call","please call","want to talk","need to talk"]

CANCEL_PHRASES = ["cancel my order","cancel the order","cancel order","cancel it","want to cancel","need to cancel","cancellation","cancel my"]

NOT_RECEIVED_PHRASES = ["not received","didn't receive","did not receive","didnt receive","haven't received","have not received","havent received",
                        "not arrived","hasn't arrived","has not arrived","not yet arrived","not delivered","where is my parcel","where is my package",
                        "where is my medicine","where is my order","track my order","order status","still waiting"]

COD_PATTERNS = ["cash on delivery","pay on delivery","payment on delivery","pay when delivered","pay after delivery"]

COLD_CHAIN_WORDS = ["cold chain","biologic","glp","insulin","ozempic","mounjaro","refrigerat","dupixent","humira","wegovy","saxenda",
                    "noveltreat","semaglutide","tirzepatide","awiqli","lantus","tresiba","novorapid","humalog","victoza","trulicity"]

# Medicine names on their own (no dose): common drug-name endings + common brands
DRUG_SUFFIX = re.compile(r"\b[a-z]{3,}(statin|pril|sartan|olol|formin|prazole|gliptin|gliflozin|dipine|cillin|mycin|floxacin|azole|tidine|lukast|mab|oxetine|pramine|tadine|parin|glitazone|amide|semide|thiazide)\b")
COMMON_BRANDS = ["panadol","lipitor","glucophage","januvia","jardiance","forxiga","crestor","concor","nexium","augmentin","xigduo","galvus",
                 "janumet","amaryl","diamicron","aztor","rosuvas","ecosprin","telma","amlong","thyronorm","eltroxin","synthroid","dolo","brufen",
                 "voltaren","zyrtec","claritin","ventolin","seretide","symbicort","plavix","eliquis","xarelto","cialis","viagra","tadacip","oxemia"]

SINGLE_BOX_HINTS = ["single box","one box","1 box","just one","only one box"]

def contains_prohibited(text: str):
    if not text:
        return None
    t = text.lower()
    for med in PROHIBITED:
        if med.lower() in t:
            return med
    for brand in BRAND_PROHIBITED:
        if brand.lower() in t:
            return brand
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
    # Check msg_type for voice/sticker even when has_media=False (some clients send type but no media flag)
    if msg_type in ["voice","audio"]:
        return ("voice_note", "auto_fallback_unsupported_type", "LOW", 90, {"type": "voice"})
    if msg_type in ["sticker","gif"]:
        return ("sticker_gif", "auto_fallback_unsupported_type", "LOW", 90, {"type": "sticker"})
    if has_media or msg_type in ["image","document"]:
        if msg_type in ["image","document"]:
            return ("prescription_image", "escalate_human_phase3_not_in_phase1", "NORMAL", 95, {"has_media": True})
    
    clean = re.sub(r"[^\w\s'\-]", "", txt).strip()   # strip punctuation/emoji for exact-match checks

    # 3. STOP / Opt-out — only whole-message commands or clear phrases
    if (clean in STOP_EXACT or any(p in txt for p in STOP_PHRASES)) and not STOP_NEGATION.search(txt):
        return ("opt_out", "auto_suppression + escalate", "HIGH", 100, {"keyword": clean})

    # 3b. START — resubscribe confirmation
    if clean in {"start","subscribe","resubscribe","unstop"}:
        return ("resubscribe", "auto_reply", "LOW", 100, {})

    # 4. ADVERSE REACTION — patient safety, before everything else clinical
    if any(k in txt for k in ADVERSE_STRONG) or (any(k in txt for k in ADVERSE_SOFT) and any(c in txt for c in ADVERSE_CONTEXT)):
        return ("adverse_reaction", "escalate_human_urgent_safety", "URGENT", 95, {})

    # 4b. Clinical question — safety escalate (but "alternative medicine" is a product category, not clinical)
    if "alternative medicine" not in txt:
        for kw in CLINICAL_KEYWORDS:
            if kw in txt and not (kw == "can i take" and CLINICAL_EXCLUDE.search(txt)):
                return ("clinical_question", "escalate_human_safety", "URGENT", 90, {"keyword": kw})

    # 4c. Thanks / ok — short acknowledgement, no escalation
    if txt in ACK_EXACT or clean in ACK_EXACT:
        return ("acknowledgement", "auto_reply", "LOW", 95, {})

    # 4d. Wants a human
    if any(p in txt for p in HUMAN_PHRASES):
        return ("human_request", "escalate_human_high", "HIGH", 90, {})
    
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
    # Allow long messages if they START with a greeting word BUT don't contain specific intent keywords
    first_words = txt.split()[:2] if txt else []
    starts_with_greeting = any(w in [v.lower() for v in GREETING_VARIANTS] for w in first_words)
    greeting_score = fuzzy_match(txt, GREETING_VARIANTS, 80)
    
    # Specific keywords that override a greeting opener
    SPECIFIC_KEYWORDS = ["dupixent","humira","wegovy","saxenda","mounjaro","ozempic","noveltreat","insulin","tramadol","xanax","shipping","payment","customs","refund","damaged","reorder","price","cost","dosage","dose"]
    has_specific = any(k in txt for k in SPECIFIC_KEYWORDS)
    
    if greeting_score >= 80 and len(txt) < 80 and not any(k in txt for k in MEDICINE_HINTS) and not has_specific:
        return ("faq_greeting", "auto_reply", "LOW", greeting_score, {})
    if starts_with_greeting and len(txt) < 80 and not has_specific and not any(k in txt for k in MEDICINE_HINTS):
        return ("faq_greeting", "auto_reply", "LOW", 85, {})
    
    # 8. Explicit intents by keywords (deterministic)
    # buy_in_india BEFORE shipping so 'ship' doesn't trigger shipping first
    if any(k in txt for k in ["buy in india myself","buy in india","i have someone in india","can you just ship","send you the medicine and you forward"]):
        return ("buy_in_india", "escalate_human_case_by_case", "NORMAL", 85, {})
    
    if any(p in txt for p in CANCEL_PHRASES):
        return ("cancel_order", "escalate_human_high", "HIGH", 90, {})

    if any(p in txt for p in NOT_RECEIVED_PHRASES):
        return ("order_status", "escalate_human_high", "HIGH", 90, {})

    if any(p in txt for p in COD_PATTERNS) or re.search(r"\bcod\b(?! liver)", txt):
        return ("payment", "escalate_human", "NORMAL", 90, {"topic": "cod"})

    if any(k in txt for k in COLD_CHAIN_WORDS):
        return ("cold_chain_biologic", "escalate_human_flag_special_shipping", "HIGH", 90, {})

    if any(k in txt for k in ["discount","price match","cheaper elsewhere","too high","too expensive","negotiate","can you lower"]):
        return ("price_negotiation", "escalate_human", "NORMAL", 85, {})

    if re.search(r"\b(customs|import|importing|imported|clearance|regulatory|approval|moh|mohap|dha|doh|duty|duties)\b", txt):
        return ("customs_import", "escalate_human", "NORMAL", 85, {})

    if any(k in txt for k in ["shipping","delivery","deliver","how long","when will","courier","tracking"]):
        return ("shipping_delivery", "escalate_human", "NORMAL", 85, {})

    if any(k in txt for k in ["payment","paid","pay","transaction","bank transfer","payment issue","paid but"]):
        return ("payment", "escalate_human_urgent", "URGENT", 85, {})
    
    if any(k in txt for k in ["otc","supplement","vitamin","berberine","protein","over the counter","cod liver","fish oil","omega",
                               "multivitamin","collagen","probiotic","melatonin","biotin","ashwagandha"]):
        return ("otc_supplement", "escalate_human_redirect_logic", "NORMAL", 85, {})
    
    if any(k in txt for k in ["complaint","return","damaged","wrong medicine","broken","leak","refund","complain"]):
        return ("complaint_return", "escalate_human_high_urgent", "URGENT" if "damaged" in txt or "wrong" in txt else "HIGH", 85, {})
    
    if any(k in txt for k in ["privacy","data","gdpr","my data","delete my"]):
        return ("privacy_data", "escalate_human", "NORMAL", 85, {})
    
    if any(k in txt for k in ["status","where is my order","order status","track my order","mfl-","reference"]):
        return ("order_status", "escalate_human_high", "HIGH", 85, {})
    
    if any(k in txt for k in ["reorder","refill","same order again","repeat order","same as last"]):
        return ("reorder", "escalate_human_normal", "NORMAL", 85, {})
    
    if any(k in txt for k in ["different from","competitor","why should i use you","instead of buying locally","amazon"]):
        return ("competitor_comparison", "auto_reply + collect", "LOW", 80, {})
    
    if any(k in txt for k in ["device","alternative medicine","ayurvedic","homeopathy","homeopathic","unani","bp monitor","glucometer","medical device","service fee"]):
        return ("medical_device_alt", "escalate_human", "NORMAL", 80, {})
    
    # 8b. Fuzzy FAQ (service / trust / off-topic) — AFTER specific keywords so loose matching can't steal them
    if fuzzy_match(txt, HOW_IT_WORKS_VARIANTS, 80) >= 80:
        return ("service_explanation", "auto_reply", "LOW", fuzzy_match(txt, HOW_IT_WORKS_VARIANTS, 80), {})
    
    if fuzzy_match(txt, TRUST_VARIANTS, 80) >= 80:
        return ("trust_question", "auto_reply", "LOW", fuzzy_match(txt, TRUST_VARIANTS, 80), {})
    
    if fuzzy_match(txt, OFF_TOPIC_VARIANTS, 80) >= 80:
        return ("off_topic", "auto_redirect", "LOW", fuzzy_match(txt, OFF_TOPIC_VARIANTS, 80), {})
    
    # 9. Medicine inquiry / Pricing — collect + escalate (most common)
    if (re.match(r"^(do you have|do u have|have you got|u have|available)\b", txt) or "is it available" in txt
            or DRUG_SUFFIX.search(txt) or any(b in txt for b in COMMON_BRANDS)):
        return ("medicine_inquiry", "collect + escalate_human", "NORMAL", 85, {})
    if any(k in txt for k in PRICING_KEYWORDS) or any(k in txt for k in MEDICINE_HINTS) or re.search(r"\b\d+\s*mg\b", txt):
        return ("medicine_inquiry", "collect + escalate_human", "NORMAL", 80, {})
    
    # 10. General fallback — escalate
    return ("general", "escalate_human", "NORMAL", 50, {})
