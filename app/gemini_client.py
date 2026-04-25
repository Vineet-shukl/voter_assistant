import os
import google.generativeai as genai
from app.prompts import build_chat_prompt, REFUSAL_TEMPLATES

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Primary model: gemini-1.5-flash — reliable, fast, low-cost
# Fallback: gemini-1.5-flash-8b — even cheaper, still solid for factual Q&A
PRIMARY_MODEL   = "gemini-1.5-flash"
FALLBACK_MODEL  = "gemini-1.5-flash-8b"

# Indian political parties/leaders — partisan refusal guard
PARTISAN_KEYWORDS = [
    "vote for", "vote bjp", "vote congress", "vote aap", "vote tmc",
    "modi", "rahul gandhi", "kejriwal", "mamata", "yogi", "nitish",
    "bjp", "congress", "aam aadmi party", "shiv sena", "ncp", "bsp", "sp",
    "endorse", "best party", "which party", "support party",
    "opinion on party", "party better", "who should i vote"
]

def check_for_refusal(message: str) -> str | None:
    lower = message.lower()
    if any(kw in lower for kw in PARTISAN_KEYWORDS):
        return REFUSAL_TEMPLATES["partisan"]
    return None


def _call_model(model_name: str, system_instruction: str, user_message: str) -> str:
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )
    response = model.generate_content(
        user_message,
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            max_output_tokens=512
        )
    )
    return response.text


def generate_reply(user_message: str, grounded_context: dict) -> str:
    """Calls Gemini only when local answer layer doesn't cover the question."""
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal

    system_instruction = build_chat_prompt(grounded_context)

    # Try primary model, fall back to cheaper model on any error
    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            return _call_model(model_name, system_instruction, user_message)
        except Exception as e:
            print(f"[VoteWise] Model {model_name} failed: {e}")
            continue  # try fallback

    # Both models failed — return friendly guidance
    return (
        "⚠️ I'm having trouble reaching the AI service right now. "
        "For immediate help, please:\n\n"
        "- 🌐 Visit [voters.eci.gov.in](https://voters.eci.gov.in)\n"
        "- 📞 Call National Voter Helpline: **1950** (toll-free, 24×7)\n"
        "- 🏛️ Visit [eci.gov.in](https://eci.gov.in) for official information"
    )
