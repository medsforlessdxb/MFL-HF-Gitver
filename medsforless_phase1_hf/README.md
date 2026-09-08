---
title: Medsforless Phase 1 - Deterministic MVP
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# Phase 1 ONLY - Deterministic MVP per Security Review Doc

**Scope per doc table Phase 1:** Webhook authentication, queue, database, FAQ, office hours, human handoff

**Exit criteria per doc:**
- ✅ No duplicate replies - `wamid` PRIMARY KEY + idempotency test
- ✅ Verified logs - `safe_log()` redacts wa_id
- ✅ Replay tests - `test_replay.py`

**Explicitly NOT in Phase 1:**
- ❌ No LLM (Phase 2)
- ❌ No media intake (Phase 3) - images escalated with note "Phase 3"
- ❌ No controlled automation (Phase 4)

### Critical Fixes implemented (from doc)
- X-Hub-Signature-256 verification BEFORE JSON parse with compare_digest
- DB-backed storage, not `conversations = {}` dict
- Iterate ALL entries/changes/messages, not [0]
- Return 5xx for transient, not 200
- Queue fast <200ms

### Endpoints
- `GET /health` - minimal
- `GET /webhook` - verification
- `POST /webhook` - main, with signature check
- `/` - Gradio dashboard proving Phase 1 exit criteria

### Env Vars (HF Secrets)
VERIFY_TOKEN=medsforless_verify_2026
META_APP_SECRET=...
GRAPH_API_VERSION=v21.0
DATABASE_PATH=/tmp/medsforless_phase1.db
