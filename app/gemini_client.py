import os
from google import genai
from google.genai import types
from app.prompts import build_chat_prompt, REFUSAL_TEMPLATES

API_KEY = os.environ.get("GEMINI_API_KEY")
_client = genai.Client(api_key=API_KEY) if API_KEY else None

# gemini-2.5-flash-lite: cheapest in the new SDK, verified working
# gemini-2.5-flash:      fallback if lite fails
PRIMARY_MODEL  = "gemini-2.5-flash-lite"
FALLBACK_MODEL = "gemini-2.5-flash"

# Indian political parties/leaders — partisan refusal guard
PARTISAN_KEYWORDS = [
    "vote bjp", "vote congress", "vote aap", "vote tmc", "vote for",
    "modi", "rahul gandhi", "kejriwal", "mamata", "yogi", "nitish",
    "bjp", "congress party", "aam aadmi party", "shiv sena", "ncp", "bsp", "sp",
    "best party", "which party", "support party", "party better",
    "who should i vote", "endorse"
]

def check_for_refusal(message: str) -> str | None:
    lower = message.lower()
    if any(kw in lower for kw in PARTISAN_KEYWORDS):
        return REFUSAL_TEMPLATES["partisan"]
    return None


def _call_model(model_name: str, system_instruction: str, user_message: str) -> str:
    if not _client:
        raise RuntimeError("GEMINI_API_KEY not configured.")
    response = _client.models.generate_content(
        model=model_name,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            max_output_tokens=512,
        )
    )
    return response.text


def generate_reply(user_message: str, grounded_context: dict) -> str:
    """Calls Gemini only when local answer layer doesn't cover the question."""
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal

    system_instruction = build_chat_prompt(grounded_context)

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            return _call_model(model_name, system_instruction, user_message)
        except Exception as e:
            print(f"[VoteWise] Model {model_name} failed: {type(e).__name__}: {e}")
            continue

    return (
        "⚠️ I'm having trouble reaching the AI service right now. "
        "For immediate help, please:\n\n"
        "- 🌐 Visit [voters.eci.gov.in](https://voters.eci.gov.in)\n"
        "- 📞 Call National Voter Helpline: **1950** (toll-free, 24×7)\n"
        "- 🏛️ Visit [eci.gov.in](https://eci.gov.in) for official information"
    )
