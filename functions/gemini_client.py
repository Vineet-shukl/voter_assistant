"""
VoteWise India — Gemini API client with Firestore caching.

Handles all AI-related logic for VoteWise India:
    - Partisan-question refusal guard
    - 24-hour Firestore response cache to minimise API costs
    - Primary / fallback model invocation via Google Generative AI SDK
    - Graceful degradation with an ECI-sourced offline message
"""

import hashlib
import logging
import os
import time
from typing import Optional

from google.cloud import firestore as firestore_client
from prompts import build_chat_prompt, REFUSAL_TEMPLATES

# ── Gemini API key ─────────────────────────────────────────────────────────────
GEMINI_API_KEY: Optional[str] = os.environ.get("GEMINI_API_KEY")

# ── Model selection ────────────────────────────────────────────────────────────
PRIMARY_MODEL: str = os.environ.get("ACTIVE_MODEL", "gemini-1.5-flash")
FALLBACK_MODEL: str = os.environ.get("FALLBACK_MODEL", "gemini-1.5-flash-8b")

# ── Firestore cache settings ──────────────────────────────────────────────────
CACHE_TTL_SECONDS: int = 60 * 60 * 24  # 24 hours

# ── Generation config ─────────────────────────────────────────────────────────
_TEMPERATURE: float = 0.2
_MAX_OUTPUT_TOKENS: int = 512

# ── Firestore singleton ───────────────────────────────────────────────────────
_db: Optional[firestore_client.Client] = None


def _get_db() -> firestore_client.Client:
    global _db
    if _db is None:
        _db = firestore_client.Client()
    return _db


# ── Partisan refusal guard ────────────────────────────────────────────────────
PARTISAN_KEYWORDS: tuple[str, ...] = (
    "vote bjp", "vote congress", "vote aap", "vote tmc", "vote for",
    "modi", "rahul gandhi", "kejriwal", "mamata", "yogi", "nitish",
    "bjp", "congress party", "aam aadmi party", "shiv sena", "ncp", "bsp", "sp",
    "best party", "which party", "support party", "party better",
    "who should i vote", "endorse",
)


def check_for_refusal(message: str) -> Optional[str]:
    lower = message.lower()
    if any(kw in lower for kw in PARTISAN_KEYWORDS):
        return REFUSAL_TEMPLATES["partisan"]
    return None


# ── Firestore cache helpers ───────────────────────────────────────────────────

def _cache_key(message: str) -> str:
    return hashlib.sha256(message.strip().lower().encode()).hexdigest()


def _read_cache(message: str) -> Optional[dict]:
    try:
        db = _get_db()
        ref = db.collection("cache").document(_cache_key(message))
        snap = ref.get()
        if snap.exists:
            data = snap.to_dict()
            age = time.time() - data.get("created_at", 0)
            if age < CACHE_TTL_SECONDS:
                ref.update({"hit_count": firestore_client.Increment(1)})
                return data
    except Exception as exc:
        logging.warning("Cache read error: %s", exc)
    return None


def _write_cache(message: str, reply: str, followups: list, source: str) -> None:
    try:
        db = _get_db()
        ref = db.collection("cache").document(_cache_key(message))
        ref.set({
            "query": message.strip().lower(),
            "reply": reply,
            "suggested_followups": followups,
            "source": source,
            "created_at": time.time(),
            "hit_count": 0,
        })
    except Exception as exc:
        logging.warning("Cache write error: %s", exc)


# ── Gemini API call ───────────────────────────────────────────────────────────

def _call_gemini(model_name: str, system_instruction: str, user_message: str) -> str:
    """Calls the Gemini API and returns the generated text."""
    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config=genai.types.GenerationConfig(
            temperature=_TEMPERATURE,
            max_output_tokens=_MAX_OUTPUT_TOKENS,
        ),
    )
    response = model.generate_content(user_message)
    return response.text


# ── Offline fallback message ──────────────────────────────────────────────────
_OFFLINE_FALLBACK: str = (
    "⚠️ I'm having trouble reaching the AI service right now. "
    "For immediate help:\n\n"
    "- 🌐 Visit [voters.eci.gov.in](https://voters.eci.gov.in)\n"
    "- 📞 Call National Voter Helpline: **1950** (toll-free)\n"
    "- 🗳️ Visit [eci.gov.in](https://eci.gov.in) for official information"
)


# ── Public entry point ────────────────────────────────────────────────────────

def generate_reply(user_message: str, grounded_context: dict) -> tuple[str, str]:
    """Generates a reply using a 3-tier strategy: refusal → cache → Gemini API."""

    # 1. Partisan guard
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal, "local"

    # 2. Firestore cache hit
    cached = _read_cache(user_message)
    if cached:
        return cached["reply"], "cache"

    # 3. No API key configured — return friendly fallback
    if not GEMINI_API_KEY:
        logging.error("[VoteWise] GEMINI_API_KEY is not set.")
        return _OFFLINE_FALLBACK, "local"

    # 4. Call Gemini API with primary then fallback model
    system_instruction = build_chat_prompt(grounded_context)
    for model_name in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            reply = _call_gemini(model_name, system_instruction, user_message)
            _write_cache(user_message, reply, [], "ai")
            return reply, "ai"
        except Exception as exc:
            logging.warning(
                "[VoteWise] Model %s failed: %s: %s",
                model_name, type(exc).__name__, exc,
            )

    return _OFFLINE_FALLBACK, "local"
