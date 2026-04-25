import os
import google.generativeai as genai
from app.prompts import build_chat_prompt, REFUSAL_TEMPLATES

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# gemini-2.0-flash-lite: cheapest, fast, great for factual Q&A — saves tokens vs 2.5-flash
MODEL_NAME = "gemini-2.0-flash-lite"

PARTISAN_KEYWORDS = [
    "vote for", "trump", "biden", "harris", "democrat", "republican",
    "endorse", "opinion on", "which party", "political party", "gop",
    "liberal", "conservative", "maga"
]

def check_for_refusal(message: str) -> str | None:
    """Keyword-based partisan/off-topic guard. Returns refusal string or None."""
    lower = message.lower()
    if any(kw in lower for kw in PARTISAN_KEYWORDS):
        return REFUSAL_TEMPLATES["partisan"]
    return None


def generate_reply(user_message: str, grounded_context: dict) -> str:
    """
    Sends message to Gemini with minimal, grounded context.
    Pre-checks reduce unnecessary API calls.
    """
    # Guard 1: Partisan check (no API call)
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal

    # Guard 2: Build a lean system prompt (only relevant context)
    system_instruction = build_chat_prompt(grounded_context)

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_instruction
        )
        response = model.generate_content(
            user_message,
            generation_config=genai.GenerationConfig(
                temperature=0.2,      # Low temp = more deterministic, fewer retry tokens
                max_output_tokens=512 # Cap response length to save tokens
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "⚠️ I'm having trouble connecting right now. Please try again or visit your state's official election website for the most accurate information."
