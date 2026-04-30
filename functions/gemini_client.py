import os
import hashlib
import time
import logging
from typing import Optional

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from google.cloud import firestore as firestore_client

from prompts import build_chat_prompt, REFUSAL_TEMPLATES

# ── Vertex AI init (lazy, called on first request) ───────────────────────────
PROJECT_ID = os.environ.get("GCLOUD_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
REGION     = os.environ.get("VERTEX_REGION", "asia-south1")
_vertex_initialized = False

def _ensure_vertex_init():
    global _vertex_initialized
    if not _vertex_initialized:
        vertexai.init(project=PROJECT_ID, location=REGION)
        _vertex_initialized = True

# ── Remote Config model selection (falls back to env / hardcoded default) ─────
PRIMARY_MODEL  = os.environ.get("ACTIVE_MODEL",   "gemini-2.5-flash-lite-preview-06-17")
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL",  "gemini-2.5-flash")

# ── Firestore (for response cache) ────────────────────────────────────────────
_db: Optional[firestore_client.Client] = None

def _get_db() -> firestore_client.Client:
    global _db
    if _db is None:
        _db = firestore_client.Client()
    return _db

# ── Partisan refusal guard ────────────────────────────────────────────────────
PARTISAN_KEYWORDS = [
    "vote bjp", "vote congress", "vote aap", "vote tmc", "vote for",
    "modi", "rahul gandhi", "kejriwal", "mamata", "yogi", "nitish",
    "bjp", "congress party", "aam aadmi party", "shiv sena", "ncp", "bsp", "sp",
    "best party", "which party", "support party", "party better",
    "who should i vote", "endorse",
]

def check_for_refusal(message: str) -> Optional[str]:
    lower = message.lower()
    if any(kw in lower for kw in PARTISAN_KEYWORDS):
        return REFUSAL_TEMPLATES["partisan"]
    return None


# ── Firestore cache helpers ───────────────────────────────────────────────────
CACHE_TTL_SECONDS = 60 * 60 * 24  # 24 hours

def _cache_key(message: str) -> str:
    return hashlib.sha256(message.strip().lower().encode()).hexdigest()

def _read_cache(message: str) -> Optional[dict]:
    try:
        db   = _get_db()
        ref  = db.collection("cache").document(_cache_key(message))
        snap = ref.get()
        if snap.exists:
            data = snap.to_dict()
            age  = time.time() - data.get("created_at", 0)
            if age < CACHE_TTL_SECONDS:
                ref.update({"hit_count": firestore_client.Increment(1)})
                return data
    except Exception as exc:
        logging.warning("Cache read error: %s", exc)
    return None

def _write_cache(message: str, reply: str, followups: list, source: str):
    try:
        db  = _get_db()
        ref = db.collection("cache").document(_cache_key(message))
        ref.set({
            "query":               message.strip().lower(),
            "reply":               reply,
            "suggested_followups": followups,
            "source":              source,
            "created_at":          time.time(),
            "hit_count":           0,
        })
    except Exception as exc:
        logging.warning("Cache write error: %s", exc)


# ── Vertex AI call ────────────────────────────────────────────────────────────
def _call_vertex(model_name: str, system_instruction: str, user_message: str) -> str:
    _ensure_vertex_init()
    model    = GenerativeModel(
        model_name,
        system_instruction=system_instruction,
    )
    gen_cfg  = GenerationConfig(temperature=0.2, max_output_tokens=512)
    response = model.generate_content(user_message, generation_config=gen_cfg)
    return response.text


# ── Public entry point ────────────────────────────────────────────────────────
def generate_reply(user_message: str, grounded_context: dict) -> tuple[str, str]:
    """Returns (reply_text, source) where source is 'local'|'cache'|'ai'."""

    # Guard: partisan refusal
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal, "local"

    # Guard: check Firestore cache
    cached = _read_cache(user_message)
    if cached:
        return cached["reply"], "cache"

    # Build prompt and call Vertex AI
    system_instruction = build_chat_prompt(grounded_context)

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            reply = _call_vertex(model_name, system_instruction, user_message)
            _write_cache(user_message, reply, [], "ai")
            return reply, "ai"
        except Exception as exc:
            logging.warning("[VoteWise] Model %s failed: %s: %s", model_name, type(exc).__name__, exc)

    fallback = (
        "⚠️ I'm having trouble reaching the AI service right now. "
        "For immediate help:\n\n"
        "- 🌐 Visit [voters.eci.gov.in](https://voters.eci.gov.in)\n"
        "- 📞 Call National Voter Helpline: **1950** (toll-free)\n"
        "- 🗳️ Visit [eci.gov.in](https://eci.gov.in) for official information"
    )
    return fallback, "local"
