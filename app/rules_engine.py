import json
import os
from typing import Dict, Any, Optional

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'election_data.json')

def load_data() -> Dict[str, Any]:
    """Loads the election data from JSON file."""
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"states": {}, "general_faqs": [], "local_answers": {}}

ELECTION_DATA = load_data()

# ---------------------------------------------------------------------------
# Local keyword-answer map — zero API tokens used for these queries
# ---------------------------------------------------------------------------
LOCAL_ANSWERS: Dict[str, tuple[list[str], str]] = {
    "age_requirement": (
        ["how old", "age to vote", "minimum age", "age requirement", "old enough"],
        "You must be **at least 18 years old** on or before Election Day to vote in the United States. Some states allow 17-year-olds to vote in primaries if they will be 18 by the general election."
    ),
    "citizenship": (
        ["citizen", "citizenship", "green card", "permanent resident", "non-citizen"],
        "You must be a **U.S. citizen** to vote in federal, state, and most local elections. Permanent residents (green card holders) are **not** eligible to vote in federal or state elections."
    ),
    "registration": (
        ["how to register", "how do i register", "register to vote", "sign up to vote", "voter registration"],
        "You can register to vote in several ways:\n- **Online** – Most states offer online registration at their Secretary of State website.\n- **By Mail** – Download, fill out, and mail a voter registration form.\n- **In Person** – Visit your local election office, DMV, or public library.\n\nDeadlines vary by state. If you know your state, ask me for the specific deadline!"
    ),
    "id": (
        ["what id", "id required", "photo id", "identification", "id do i need", "bring to polls"],
        "ID requirements vary by state:\n- **Strict Photo ID states** (e.g., TX, FL): You must show a government-issued photo ID.\n- **Non-strict states** (e.g., CA, NY, IL): Photo ID is generally not required, but first-time voters who registered by mail may need to provide ID.\n\nAlways check your specific state's rules! Ask me about your state (e.g., 'what ID do I need in Texas?')."
    ),
    "absentee": (
        ["absentee", "mail-in", "mail ballot", "vote by mail", "mail in ballot"],
        "**Voting by mail (absentee)** is available in all 50 states:\n- **No-excuse mail voting**: Many states (like CA, NY) let anyone request a mail ballot without a reason.\n- **Excuse-required states** (like TX): You need a specific reason (illness, travel, disability) to vote absentee.\n\nRequest your mail ballot early — they usually need to be requested weeks before Election Day."
    ),
    "early_voting": (
        ["early voting", "vote early", "before election day", "early poll"],
        "**Early voting** allows you to cast your ballot before Election Day at designated polling locations. Most states offer 1–2 weeks of early voting. Some states with no dedicated early voting period do allow in-person absentee voting. Ask me about your state's specific early voting dates!"
    ),
    "election_day": (
        ["when is election day", "election day date", "when do i vote", "when is the election"],
        "**Election Day** in the United States is the **first Tuesday after the first Monday in November** for federal elections. For 2024, that is **November 5, 2024**.\n\nPolls typically open between 6–8 AM and close between 7–9 PM (local time). Check your specific polling place hours."
    ),
    "polling_place": (
        ["where to vote", "polling place", "polling location", "find my polling", "where is my poll"],
        "To find your polling place:\n1. **Google** 'polling place [your city/state]'\n2. Visit your **state's Secretary of State website**\n3. Use **vote.gov** — it links to your state's official lookup tool\n\nYou must vote at your assigned polling location unless you're voting early or by mail."
    ),
    "deadline": (
        ["registration deadline", "when to register", "last day to register", "deadline to register"],
        "Registration deadlines vary by state — from 30 days before the election to **same-day registration** in some states.\n\nTell me your state (e.g., 'what is the deadline in California?') and I'll give you the specific date from my data!"
    ),
    "felony": (
        ["felony", "criminal record", "prison", "incarcerated", "disenfranchised", "conviction"],
        "Voting rights for people with felony convictions vary by state:\n- **Most states**: Rights are restored after completing your sentence (including parole/probation).\n- **Some states** (like Maine and Vermont): You can vote even while incarcerated.\n- **Other states**: May require waiting periods or applications to restore voting rights.\n\nCheck your state's Secretary of State website for exact rules."
    ),
}

def find_local_answer(message: str) -> Optional[str]:
    """
    Scans the message for known keywords and returns a pre-built answer.
    Returns None if no local answer is found (i.e., Gemini should be called).
    """
    lower = message.lower()
    for _key, (keywords, answer) in LOCAL_ANSWERS.items():
        if any(kw in lower for kw in keywords):
            return answer
    return None


def check_eligibility(age: int, citizen: bool, state: str) -> Dict[str, Any]:
    """Determines voter eligibility based on age and citizenship."""
    eligible = True
    reasons = []
    next_steps = []

    if not citizen:
        eligible = False
        reasons.append("You must be a U.S. citizen to vote in federal and state elections.")

    if age < 18:
        eligible = False
        reasons.append(f"You are {age} years old. You must be at least 18 years old to vote.")

    if eligible:
        reasons.append("✅ You meet the basic age and citizenship requirements.")
        next_steps.append("Check your voter registration status.")
        next_steps.append("Find your polling place or request a mail ballot.")
        next_steps.append("Check your state's registration deadline.")
    else:
        next_steps.append("Wait until you meet the requirements.")
        next_steps.append("Learn about civic engagement opportunities in your community.")

    return {"eligible": eligible, "reasons": reasons, "next_steps": next_steps}


def get_deadlines(state: str) -> Dict[str, Any]:
    """Returns election deadlines for a given state code."""
    state_upper = state.upper()
    state_data = ELECTION_DATA.get("states", {}).get(state_upper)
    if not state_data:
        return {"error": f"No data found for state code: {state_upper}"}
    return {
        "state_name": state_data.get("name"),
        "registration_deadline": state_data.get("registration_deadline"),
        "early_voting_start": state_data.get("early_voting_start"),
        "early_voting_end": state_data.get("early_voting_end"),
        "election_day": state_data.get("election_day"),
    }


def get_state_rules(state: str) -> Dict[str, Any]:
    """Returns voting rules and methods for a given state code."""
    state_upper = state.upper()
    state_data = ELECTION_DATA.get("states", {}).get(state_upper)
    if not state_data:
        return {"error": f"No data found for state code: {state_upper}"}
    return {
        "state_name": state_data.get("name"),
        "id_required": state_data.get("id_required"),
        "voting_methods": state_data.get("voting_methods"),
        "registration_methods": state_data.get("registration_methods"),
        "official_url": state_data.get("official_url"),
    }
