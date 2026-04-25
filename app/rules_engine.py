import json
import os
from typing import Dict, Any

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'election_data.json')

def load_data() -> Dict[str, Any]:
    """Loads the election data from JSON file."""
    try:
        with open(DATA_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"states": {}, "general_faqs": []}

ELECTION_DATA = load_data()

def check_eligibility(age: int, citizen: bool, state: str) -> Dict[str, Any]:
    """
    Determines if a user is eligible to vote based on age and citizenship.
    In the US, you must be a citizen and 18 years or older on election day.
    For simplicity, we check if age >= 18.
    """
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
        reasons.append("You meet the age and citizenship requirements.")
        next_steps.append("Check your voter registration status.")
        next_steps.append("Find your polling place or request a mail ballot.")
    else:
        next_steps.append("Wait until you meet the requirements.")
        next_steps.append("Learn more about civic engagement opportunities in your community.")

    return {
        "eligible": eligible,
        "reasons": reasons,
        "next_steps": next_steps
    }

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
        "election_day": state_data.get("election_day")
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
        "official_url": state_data.get("official_url")
    }
