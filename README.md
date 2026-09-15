
# Medsforless — Phase 1 v1.1 Deterministic MVP

**QA Scenarios v1.1 — 22 intents | Security Review Compliant | Deterministic, No LLM**

> Architecture + Flow + Comments PDF: See `docs/` folder (generated from review)

![Architecture](https://raw.githubusercontent.com/your-org/medsforless/main/docs/architecture.png)

## Scope per Security Review Doc (Sep 2026)

**Phase 1 (NOW):** Webhook authentication (HMAC X-Hub-Signature-256), queue (<200ms), database (wamid PRIMARY KEY), FAQ auto-reply (5 intents), office hours 9AM-11PM Asia/Dubai, human handoff (17 intents), suppression table, audit logs

**Exit Criteria:** No duplicate replies (wamid PK test), Verified redacted logs (safe_log), Replay tests pass

**Explicitly NOT in Phase 1:** No LLM (Phase 2), No media intake/OCR (Phase 3), No auto PDF quotes (Phase 4-6)

## 22 QA Intents Implemented (v1.1)

| # | QA Scenario | Phase 1 Action | Priority |
|---|-------------|----------------|----------|
| 1 | First Contact / Greetings — ANY opener | Auto-Reply | LOW |
| 2 | How It Works / Service Explanation | Auto-Reply | LOW |
| 3 | Pricing Questions | Collect + Escalate | NORMAL |
| 4 | Medicine Inquiries General | Collect + Escalate | NORMAL |
| 5 | Prescription Handling — photo | Escalate — Phase 3 not in Phase 1 | NORMAL |
| 6 | Shipping & Delivery | Escalate | NORMAL |
| 7 | Payment | Escalate | URGENT |
| 8 | Customs & Import | Escalate | NORMAL |
| 9 | Controlled Substances BLOCK | Auto BLOCK + Audit | HIGH |
| 10 | OTC / Supplements | Escalate + Redirect | NORMAL |
| 11 | Cold Chain / Biologics / GLP-1 | Escalate Flag | HIGH |
| 12 | Medical Devices / Alt Medicine | Escalate | NORMAL |
| 13 | Single Box Warning | Auto Warning + Escalate | NORMAL |
| 14 | Order Status | Escalate | HIGH |
| 15 | Complaints & Returns | Escalate | URGENT/HIGH |
| 16 | Privacy & Data | Escalate | NORMAL |
| 17 | Opt-Out / STOP | Suppression Table | HIGH |
| 18 | Off-Topic | Auto Redirect | LOW |
| 19 | Escalation to Human | Escalate | Per definition |
| 20 | Reorder / Repeat | Escalate | NORMAL |
| 21 | Buy in India Themselves | Escalate Case-by-Case | NORMAL |
| 22 | Competitor Comparison | Auto + Collect | LOW |
| + | Voice / Sticker / GIF | Auto Fallback | LOW |
| + | Arabic/Hindi/Urdu | Auto English Request | NORMAL |

## Project Structure (GitHub)

```
.
├── app/
│   ├── main.py              # FastAPI webhook + Gradio dashboard mount
│   ├── config.py            # Env config
│   ├── security.py          # HMAC verify (constant_time), safe_log redaction, office hours
│   ├── database.py          # SQLite wamid PK, jobs, suppressions, audit, retention 7d
│   ├── classifier.py        # Deterministic 22 intents with rapidfuzz 80/85, blocklist first
│   ├── templates.py         # QA v1.1 response templates (<4 paras, Rule #10)
│   └── prohibited_meds.json # 36 controlled substances BLOCK list
├── tests/
│   └── test_replay.py       # Exit criteria: idempotency, redacted logs, QA classifier
├── data/                    # SQLite DB (gitignored)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Security Fixes Implemented (per Review Doc)

- ✅ `X-Hub-Signature-256` verification with `hmac.compare_digest` BEFORE JSON parse
- ✅ DB-backed `messages.wamid PRIMARY KEY` — not `conversations = {}` dict
- ✅ Iterate ALL `entry → changes → messages` — not just `[0]`
- ✅ Idempotency: duplicate wamid blocked → no duplicate replies
- ✅ Return 5xx for transient failures so Meta retries, not 200
- ✅ Fast webhook <200ms: validate, persist, enqueue, return 200
- ✅ `GRAPH_API_VERSION` from env, not hard-coded v18.0
- ✅ Redacted logs via `safe_log()` — no wa_id/PHI in plaintext
- ✅ `health` minimal, STOP suppression table, office hours 9AM-11PM

## Quick Start (GitHub — Local)

```bash
git clone https://github.com/your-org/medsforless.git
cd medsforless
cp .env.example .env
# Edit .env with your Meta secrets
pip install -r requirements.txt
python -m app.main
# Open http://localhost:8000/ for Gradio dashboard + human buckets
# Open http://localhost:8000/health for health check
# Webhook URL for Meta: https://your-domain.com/webhook
```

## Docker

```bash
docker-compose up --build
# App runs at http://localhost:8000
# Data persists in ./data/
```

## Environment Variables

```
VERIFY_TOKEN=medsforless_verify_2026
META_APP_SECRET=your_meta_app_secret_from_meta_developers
WHATSAPP_TOKEN=your_whatsapp_cloud_api_token
PHONE_NUMBER_ID=your_phone_number_id
GRAPH_API_VERSION=v21.0
DATABASE_PATH=./data/medsforless_phase1.db
```

## Testing

```bash
pytest tests/test_replay.py -v
# Or
python tests/test_replay.py

# In Gradio UI:
# - Click "Process Message" to test 22 QA intents
# - Click "Test Idempotency" to prove PRIMARY KEY
# - Click "Test All 22 QA Scenarios v1.1" for full suite
```

## Deployment Notes

- **For GitHub:** Use Docker image + env secrets. Set `VERIFY_TOKEN` same in Meta Developer Portal and `.env`.
- **For production:** Put behind HTTPS (Meta requires HTTPS for webhook), use managed DB later (Phase 2), set retention job to delete `retention_until` expired rows.
- **For Hugging Face:** Previous version had `sdk: gradio` frontmatter and `spaces` lib. For GitHub, we use pure FastAPI + Gradio mount without `spaces.GPU` decorator.

## Flow (12 Steps)

1. Meta POST → /webhook with JSON + X-Hub-Signature-256
2. Verify HMAC constant_time BEFORE parse
3. Iterate ALL entry/changes/messages
4. Check wamid PK for duplicate
5. Insert with content_redacted via safe_log + retention_until +7d
6. Enqueue job + return 200 in <200ms
7. Worker: check suppressions, office hours
8. Deterministic classify per QA v1.1 (blocklist FIRST, then media → STOP → voice/sticker → clinical → fuzzy FAQ 80 → medicine/pricing → general)
9. If FAQ auto → template per QA v1.1 (<4 paras, ends with question)
10. Else escalate with priority URGENT/HIGH/NORMAL/LOW per QA doc
11. Send via Graph API (Phase 1 logs only, human sends in Phase 4-6)
12. Audit log + contacts update

## Comments Review Summary

See `MFL_Phase1_Comments_Review.md` and PDF in previous artifact. Key points:
- Excellent: Any greeting = greeting, never share pricing in chat (PDF only), never name pharmacy, blocklist in config, formatting Rules 1-13, escalation priorities, voice/sticker fallback, language handling.
- Critical Gaps Fixed: Typo tolerance via rapidfuzz 80/85 not LLM, prescription images escalate Phase 3 not in Phase 1 (no Claude Vision), pricing collect+escalate no Sheets, controlled BLOCK via prohibited_meds.json, single box warning, suppression table, reorder escalate.
- Missing: 24h window templates, failed delivery retries, multiple medicines parsing, Arabic medicine names, duplicate business dedup, adverse reaction template.

*Engineering review only, not legal/medical advice. Get UAE pharmacy compliance sign-off before prod. Bot collects information, you make decisions. Never let bot send quote without review until Phase 6.*

## License
Private — Medsforless
