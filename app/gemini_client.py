import os
import google.generativeai as genai
from app.prompts import build_chat_prompt, REFUSAL_TEMPLATES

API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.0-flash-lite"

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


def generate_reply(user_message: str, grounded_context: dict) -> str:
    """Calls Gemini only when local answer layer doesn't cover the question."""
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal

    system_instruction = build_chat_prompt(grounded_context)

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
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
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "⚠️ I'm having trouble connecting right now. Please visit [eci.gov.in](https://eci.gov.in) or call the National Voter Helpline at **1950** (toll-free) for assistance."
