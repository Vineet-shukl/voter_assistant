from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

load_dotenv()

from app.models import ChatRequest, ChatResponse, EligibilityResponse
from app.rules_engine import (
    check_eligibility, get_deadlines, get_state_rules,
    find_local_answer, ELECTION_DATA
)
from app.gemini_client import generate_reply

app = FastAPI(title="VoteWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="static"), name="assets")

# ----- Smart follow-up chips based on reply content -----
def pick_followups(reply: str) -> list[str]:
    r = reply.lower()
    if "register" in r:
        return ["What's the deadline to register?", "Can I register online?", "What ID do I need?"]
    if "deadline" in r or "date" in r:
        return ["How do I register?", "Where do I vote?", "Can I vote by mail?"]
    if "mail" in r or "absentee" in r:
        return ["When will my ballot arrive?", "How do I return my ballot?", "What's the deadline?"]
    if "id" in r or "identification" in r:
        return ["What if I don't have ID?", "Can I vote without ID?", "How do I register?"]
    return ["Am I eligible to vote?", "How do I register?", "What ID do I need?"]


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    context = dict(request.context or {})
    message = request.message.strip()

    # === Layer 1: Local keyword answer (0 API tokens) ===
    local_reply = find_local_answer(message)
    if local_reply:
        return ChatResponse(
            reply=local_reply,
            suggested_followups=pick_followups(local_reply),
            source="local"
        )

    # === Layer 2: Rules Engine enrichment (structured data) ===
    state = context.get("state")
    if state and isinstance(state, str) and len(state) == 2:
        deadlines = get_deadlines(state)
        rules = get_state_rules(state)
        if "error" not in deadlines:
            context["state_deadlines"] = deadlines
        if "error" not in rules:
            context["state_rules"] = rules

    # === Layer 3: Gemini (only for complex / state-specific queries) ===
    reply = generate_reply(message, context)

    return ChatResponse(
        reply=reply,
        suggested_followups=pick_followups(reply),
        source="ai"
    )


@app.get("/eligibility", response_model=EligibilityResponse)
async def eligibility_endpoint(
    age: int = Query(..., ge=0, le=150),
    citizen: bool = Query(...),
    state: str = Query(..., min_length=2, max_length=2)
):
    return EligibilityResponse(**check_eligibility(age, citizen, state.upper()))


@app.get("/timeline")
async def timeline_endpoint(state: str = Query(..., min_length=2, max_length=2)):
    deadlines = get_deadlines(state.upper())
    if "error" in deadlines:
        raise HTTPException(status_code=404, detail=deadlines["error"])
    return deadlines


@app.get("/states")
async def list_states():
    """Returns the list of supported state codes for the UI dropdown."""
    return {"states": list(ELECTION_DATA.get("states", {}).keys())}
