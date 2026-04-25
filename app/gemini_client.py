import os
import google.generativeai as genai
from app.prompts import build_chat_prompt, REFUSAL_TEMPLATES

# Initialize Gemini SDK
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

def check_for_refusal(message: str) -> str | None:
    """Basic keyword check to trigger early refusal for partisan/off-topic content."""
    lower_msg = message.lower()
    partisan_keywords = ["vote for", "trump", "biden", "democrat", "republican", "endorse", "opinion on"]
    if any(word in lower_msg for word in partisan_keywords):
        return REFUSAL_TEMPLATES["partisan"]
    
    # We let Gemini handle more nuanced off-topic refusals via the system prompt
    return None

def generate_reply(user_message: str, grounded_context: dict) -> str:
    """Sends the grounded prompt and user message to Gemini and returns the reply."""
    
    # 1. Quick safety check
    refusal = check_for_refusal(user_message)
    if refusal:
        return refusal
        
    # 2. Build system instruction
    system_instruction = build_chat_prompt(user_message, grounded_context)
    
    try:
        # 3. Call Gemini
        # Using the system_instruction feature available in recent gemini models
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_instruction
        )
        
        response = model.generate_content(
            user_message,
            generation_config=genai.GenerationConfig(
                temperature=0.3, # Keep it deterministic and factual
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "I'm currently experiencing technical difficulties connecting to my AI brain. Please try again later or check your state's official election website."
