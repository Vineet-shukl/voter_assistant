from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

import os

# Load environment variables
load_dotenv()

from app.models import ChatRequest, ChatResponse, EligibilityRequest, EligibilityResponse
from app.rules_engine import check_eligibility, get_deadlines, get_state_rules, ELECTION_DATA
from app.gemini_client import generate_reply

app = FastAPI(title="VoteWise API", description="API for the VoteWise Election Process Assistant")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the 'static' directory
# We mount it at /assets so the root / can serve index.html directly
app.mount("/assets", StaticFiles(directory="static"), name="assets")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    context = request.context or {}
    
    # Enrich context using the rules engine if state is provided
    state = context.get("state")
    if state and isinstance(state, str) and len(state) == 2:
        deadlines = get_deadlines(state)
        rules = get_state_rules(state)
        if "error" not in deadlines:
            context["state_deadlines"] = deadlines
        if "error" not in rules:
            context["state_rules"] = rules
            
    # Include generic FAQs
    context["general_faqs"] = ELECTION_DATA.get("general_faqs", [])
            
    reply = generate_reply(request.message, context)
    
    # Generate some simple followups based on the text length or generic ones
    followups = ["How do I register?", "What ID do I need?"]
    if "register" in reply.lower():
        followups = ["When is the deadline?", "Can I register online?"]
        
    return ChatResponse(reply=reply, suggested_followups=followups)

@app.get("/eligibility", response_model=EligibilityResponse)
async def eligibility_endpoint(
    age: int = Query(..., ge=0, le=150),
    citizen: bool = Query(...),
    state: str = Query(..., min_length=2, max_length=2)
):
    result = check_eligibility(age, citizen, state.upper())
    return EligibilityResponse(**result)

@app.get("/timeline")
async def timeline_endpoint(state: str = Query(..., min_length=2, max_length=2)):
    deadlines = get_deadlines(state.upper())
    if "error" in deadlines:
        raise HTTPException(status_code=404, detail=deadlines["error"])
    return deadlines
