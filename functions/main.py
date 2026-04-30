"""
VoteWise India — Firebase Cloud Functions (Gen 2)
Replaces FastAPI backend. All endpoints are HTTPS-triggered functions.
"""
import json
import logging
import os
import time
from typing import Optional

import firebase_admin
from firebase_admin import auth, firestore
from firebase_functions import https_fn, options

# Local modules (same package)
from rules_engine import (
    check_eligibility, get_deadlines, get_state_rules,
    find_local_answer, ELECTION_DATA,
)
from gemini_client import generate_reply

# ── Firebase Admin init (singleton) ──────────────────────────────────────────
if not firebase_admin._apps:
    firebase_admin.initialize_app()

_db: Optional[object] = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.client()
    return _db


# ── CORS headers ──────────────────────────────────────────────────────────────
CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}

REGION = options.SupportedRegion.ASIA_SOUTH1   # Mumbai — closest to India


# ── Auth + Rate Limiting ──────────────────────────────────────────────────────
RATE_LIMIT = 30   # max requests per hour per anonymous UID

def _verify_and_rate_limit(request: https_fn.Request) -> tuple[Optional[str], Optional[https_fn.Response]]:
    """
    Verifies Firebase ID token if present, applies rate limiting.
    If no token provided, uses IP-based UID (anonymous session).
    Returns (uid, None) on success, (None, error_response) on rate limit.
    """
    import hashlib
    auth_header = request.headers.get("Authorization", "")

    uid = None
    if auth_header.startswith("Bearer "):
        id_token = auth_header.split("Bearer ")[1]
        try:
            decoded = auth.verify_id_token(id_token)
            uid = decoded["uid"]
        except Exception as exc:
            logging.warning("Token verification failed: %s", exc)
            # Fall through to IP-based rate limiting

    # If no valid Firebase token, use IP hash as anonymous session key
    if not uid:
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
        uid = "anon-" + hashlib.sha256(ip.encode()).hexdigest()[:16]

    # Rate limiting via Firestore counter
    db  = get_db()
    ref = db.collection("rate_limits").document(uid)

    @firestore.transactional
    def _check_limit(transaction):
        snap = ref.get(transaction=transaction)
        now  = time.time()
        if snap.exists:
            data        = snap.to_dict()
            window_start = data.get("window_start", 0)
            count        = data.get("count", 0)
            if now - window_start < 3600:
                if count >= RATE_LIMIT:
                    return False
                transaction.update(ref, {"count": count + 1})
                return True
        transaction.set(ref, {"window_start": now, "count": 1})
        return True

    try:
        allowed = _check_limit(db.transaction())
    except Exception as exc:
        logging.warning("Rate limit check error: %s", exc)
        allowed = True   # fail open — don't block users on DB errors

    if not allowed:
        return None, https_fn.Response(
            json.dumps({"error": "Rate limit exceeded. Try again in an hour."}),
            status=429, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    return uid, None



# ── Analytics writer ─────────────────────────────────────────────────────────
def _log_chat(uid: str, message: str, source: str, state: Optional[str],
              language: str, response_time_ms: int):
    try:
        db = get_db()
        db.collection("analytics").document("chats").collection("entries").add({
            "session_id":        uid,
            "message":           message,
            "reply_source":      source,
            "state":             state,
            "language":          language,
            "timestamp":         firestore.SERVER_TIMESTAMP,
            "response_time_ms":  response_time_ms,
        })
    except Exception as exc:
        logging.warning("Analytics write error: %s", exc)


# ── Follow-up chips ───────────────────────────────────────────────────────────
def pick_followups(reply: str) -> list[str]:
    r = reply.lower()
    if "form 6" in r or "register" in r:
        return ["What documents for Form 6?", "Can I register online?", "Where is my BLO?"]
    if "epic" in r or "voter id" in r:
        return ["How to get e-EPIC?", "How to correct Voter ID?", "Lost my Voter ID?"]
    if "evm" in r or "vvpat" in r:
        return ["Is EVM safe?", "What is VVPAT?", "How to use EVM?"]
    if "unable" in r or "cannot vote" in r:
        return ["How to register now?", "Name not on list?", "What ID do I need?"]
    if "lok sabha" in r:
        return ["What is Vidhan Sabha?", "How many Lok Sabha seats?", "Next general election?"]
    return ["How do I register?", "What is EPIC?", "Find my polling booth?"]


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD FUNCTION: /chat
# ═══════════════════════════════════════════════════════════════════════════════
@https_fn.on_request(region=REGION, memory=options.MemoryOption.MB_512, timeout_sec=120)
def chat(request: https_fn.Request) -> https_fn.Response:
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=CORS_HEADERS)

    uid, err = _verify_and_rate_limit(request)
    if err:
        return err

    try:
        body    = request.get_json(silent=True) or {}
        message = str(body.get("message", "")).strip()
        context = dict(body.get("context", {}))
    except Exception:
        return https_fn.Response(
            json.dumps({"error": "Invalid JSON body"}),
            status=400, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    if not message:
        return https_fn.Response(
            json.dumps({"error": "message field is required"}),
            status=400, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    t0 = time.time()

    # Layer 1: local keyword answer
    local_reply = find_local_answer(message)
    if local_reply:
        followups = pick_followups(local_reply)
        _log_chat(uid, message, "local", context.get("state"), context.get("language", "English"),
                  int((time.time() - t0) * 1000))
        return https_fn.Response(
            json.dumps({"reply": local_reply, "suggested_followups": followups, "source": "local"}),
            status=200, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    # Layer 2: rules engine enrichment
    state = context.get("state")
    if state and isinstance(state, str) and len(state) == 2:
        deadlines = get_deadlines(state)
        rules     = get_state_rules(state)
        if "error" not in deadlines:
            context["state_deadlines"] = deadlines
        if "error" not in rules:
            context["state_rules"] = rules

    # Layer 3: Vertex AI Gemini (with Firestore cache)
    reply, source = generate_reply(message, context)
    followups     = pick_followups(reply)

    _log_chat(uid, message, source, state, context.get("language", "English"),
              int((time.time() - t0) * 1000))

    return https_fn.Response(
        json.dumps({"reply": reply, "suggested_followups": followups, "source": source}),
        status=200, headers={**CORS_HEADERS, "Content-Type": "application/json"}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD FUNCTION: /eligibility
# ═══════════════════════════════════════════════════════════════════════════════
@https_fn.on_request(region=REGION, memory=options.MemoryOption.MB_512, timeout_sec=30)
def eligibility(request: https_fn.Request) -> https_fn.Response:
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=CORS_HEADERS)

    uid, err = _verify_and_rate_limit(request)
    if err:
        return err

    try:
        age     = int(request.args.get("age", -1))
        citizen = request.args.get("citizen", "false").lower() == "true"
        state   = str(request.args.get("state", "DL")).upper()
    except ValueError:
        return https_fn.Response(
            json.dumps({"error": "Invalid query parameters"}),
            status=400, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    if not (0 <= age <= 150):
        return https_fn.Response(
            json.dumps({"error": "age must be between 0 and 150"}),
            status=422, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    result = check_eligibility(age, citizen, state)
    return https_fn.Response(
        json.dumps(result),
        status=200, headers={**CORS_HEADERS, "Content-Type": "application/json"}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD FUNCTION: /timeline
# ═══════════════════════════════════════════════════════════════════════════════
@https_fn.on_request(region=REGION, memory=options.MemoryOption.MB_512, timeout_sec=30)
def timeline(request: https_fn.Request) -> https_fn.Response:
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=CORS_HEADERS)

    state = str(request.args.get("state", "")).upper()
    if len(state) != 2:
        return https_fn.Response(
            json.dumps({"error": "state must be a 2-letter code (e.g. DL, MH)"}),
            status=400, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )

    deadlines = get_deadlines(state)
    if "error" in deadlines:
        return https_fn.Response(
            json.dumps(deadlines),
            status=404, headers={**CORS_HEADERS, "Content-Type": "application/json"}
        )
    return https_fn.Response(
        json.dumps(deadlines),
        status=200, headers={**CORS_HEADERS, "Content-Type": "application/json"}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD FUNCTION: /states
# ═══════════════════════════════════════════════════════════════════════════════
@https_fn.on_request(region=REGION, memory=options.MemoryOption.MB_512, timeout_sec=10)
def states(request: https_fn.Request) -> https_fn.Response:
    if request.method == "OPTIONS":
        return https_fn.Response("", status=204, headers=CORS_HEADERS)
    # Public endpoint — no auth required
    state_list = list(ELECTION_DATA.get("states", {}).keys())
    return https_fn.Response(
        json.dumps({"states": state_list}),
        status=200, headers={**CORS_HEADERS, "Content-Type": "application/json"}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLOUD FUNCTION: /health
# ═══════════════════════════════════════════════════════════════════════════════
@https_fn.on_request(region=REGION, memory=options.MemoryOption.MB_512, timeout_sec=10)
def health(request: https_fn.Request) -> https_fn.Response:
    # Public endpoint — no auth required
    return https_fn.Response(
        json.dumps({"status": "ok", "backend": "firebase-functions"}),
        status=200, headers={**CORS_HEADERS, "Content-Type": "application/json"}
    )
