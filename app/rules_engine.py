import json
import os
from typing import Dict, Any, Optional

DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'election_data.json')

def load_data() -> Dict[str, Any]:
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"states": {}, "general_faqs": [], "general_info": {}}

ELECTION_DATA = load_data()

# ---------------------------------------------------------------------------
# Local keyword-answer map for India — zero API tokens for these queries
# ---------------------------------------------------------------------------
LOCAL_ANSWERS: Dict[str, tuple[list[str], str]] = {
    "age_requirement": (
        ["how old", "age to vote", "minimum age", "age requirement", "old enough", "kitni age"],
        "**आयु पात्रता / Age Eligibility:**\nYou must be **at least 18 years old** on the 1st January of the qualifying year to enroll as a voter in India.\n\n- If you turn 18 on or before Jan 1 of the reference year, you can register that year.\n- Servicemen and their wives have special provisions."
    ),
    "citizenship": (
        ["citizen", "citizenship", "nri", "overseas", "foreign national", "oci", "nri vote"],
        "**Citizenship & Voting in India:**\n- Only **Indian citizens** can vote in Indian elections.\n- OCI (Overseas Citizen of India) card holders **cannot vote**.\n- **NRI (Non-Resident Indians)** who are Indian citizens CAN vote — register using **Form 6A** at [voters.eci.gov.in](https://voters.eci.gov.in) or at the Indian Embassy/Consulate."
    ),
    "registration": (
        [
            "how to register", "how do i register", "register to vote", "voter registration",
            "naama darz", "form 6", "enrollment", "enroll", "register myself",
            "get registered", "sign up to vote", "apply for voter",
            # missed/late registration queries
            "forgot to register", "forget to register", "forgot register",
            "missed registration", "missed to register", "didn't register",
            "did not register", "haven't registered", "not registered yet",
            "late registration", "can i still register", "still register",
            "registration deadline", "last date register",
        ],
        "**Voter Registration in India:**\nRegister online or offline using **Form 6** (new voters):\n\n1. **Online:** Visit [voters.eci.gov.in](https://voters.eci.gov.in) → 'New Registration'\n2. **Offline:** Visit your nearest BLO (Booth Level Officer) or Electoral Registration Officer\n3. **Via App:** Download the **Voter Helpline App** (Android/iOS)\n\n📌 **Documents needed:** Age proof, address proof, and one recent passport-size photograph.\n\n> ⏰ **Missed the deadline?** Registration is a continuous process in India. You can apply **any time** — ECI conducts **quarterly summary revisions** (Jan, Apr, Jul, Oct). Your name will appear on the roll after the next revision.\n\n📞 **Helpline:** 1950 (toll-free) | 🌐 [voters.eci.gov.in](https://voters.eci.gov.in)"
    ),
    "voter_id": (
        ["voter id", "epic card", "voter card", "matdata pehchan", "what is epic", "voter identity"],
        "**EPIC — Electors Photo Identity Card:**\nThe EPIC (Voter ID Card) is India's official voter identity document issued by the **Election Commission of India (ECI)**.\n\n- Apply or download at [voters.eci.gov.in](https://voters.eci.gov.in)\n- You can now get a **digital Voter ID (e-EPIC)** on your phone!\n- Apply for corrections or replacement using **Form 8**"
    ),
    "alternative_id": (
        ["alternative id", "no voter id", "without voter id", "other id", "what if i don't have", "12 documents", "aadhaar to vote"],
        "**Alternative ID at Polling Booth:**\nIf you don't have your EPIC (Voter ID), the ECI accepts **12 alternative documents**:\n\n1. Aadhaar Card\n2. Passport\n3. Driving License\n4. PAN Card\n5. MNREGA Job Card\n6. Bank/Post Office Passbook with Photo\n7. Health Insurance Smart Card (Ministry of Labour)\n8. Disability Certificate with Photo\n9. Service ID Card (Govt/PSU)\n10. Unique Disability ID (UDID) Card\n11. NPR Smart Card\n12. Smart Card issued by RGI under NPR\n\n*Your name must be on the electoral roll to vote.*"
    ),
    "evm": (
        ["evm", "electronic voting machine", "vvpat", "ballot", "voting machine", "how to vote", "voting process"],
        "**How Voting Works in India — EVM & VVPAT:**\n\n1. 🗳️ India uses **Electronic Voting Machines (EVMs)** — no paper ballot needed.\n2. 📄 Every EVM is paired with a **VVPAT (Voter Verified Paper Audit Trail)** machine that shows you a printed slip of your vote for 7 seconds before it drops into a sealed box.\n3. Show your EPIC (or alternative ID) to the polling officer.\n4. Your finger is marked with **indelible ink** after voting.\n5. Press the button next to your chosen candidate's name and symbol on the EVM."
    ),
    "check_name": (
        ["check my name", "am i registered", "electoral roll", "voter list", "find my name", "search voter"],
        "**How to Check if Your Name is on the Electoral Roll:**\n\n1. 🌐 **Online:** Visit [electoralsearch.eci.gov.in](https://electoralsearch.eci.gov.in)\n2. 📱 **App:** Download the **Voter Helpline App**\n3. 📞 **Call:** Dial **1950** (National Voter Helpline — toll-free)\n4. 🏛️ **Offline:** Visit your Booth Level Officer (BLO) or Electoral Registration Office\n\nYou'll need your name, date of birth, and state/constituency details."
    ),
    "polling_booth": (
        ["where to vote", "polling booth", "polling station", "find polling", "kahan vote", "booth location"],
        "**How to Find Your Polling Booth:**\n\n1. 🌐 Visit [voters.eci.gov.in](https://voters.eci.gov.in) → 'Know Your Polling Station'\n2. 📱 Use the **Voter Helpline App**\n3. 📞 Call **1950** (National Voter Helpline)\n4. Check the **slip sent by your BLO** before elections\n\nYour polling booth is determined by your registered residential address."
    ),
    "model_code": (
        ["model code", "mcc", "adarsh achaar", "conduct rules", "election rules during election"],
        "**Model Code of Conduct (MCC):**\nThe MCC is a set of guidelines issued by the **Election Commission of India** that comes into force once an election schedule is announced.\n\n**Key rules:**\n- No new government schemes/freebies can be announced\n- Ruling party cannot misuse government machinery\n- No religious/caste-based appeals for votes\n- Polling booths must be at least 200m from religious places\n\nViolations can be reported on the **cVIGIL app** or by calling **1950**."
    ),
    "cvigil": (
        ["cvigil", "c-vigil", "report violation", "election complaint", "mcc violation", "bribery voting"],
        "**cVIGIL App — Report Election Violations:**\nThe ECI's **cVIGIL app** lets citizens report Model Code of Conduct (MCC) violations in real-time with photo/video evidence.\n\n📱 Download: Available on **Google Play Store** and **Apple App Store**\n✅ Reports are geotagged and action is taken within **100 minutes**\n📋 You can track your complaint status in the app\n\nCommon violations to report: voter bribery, illegal rallies, defacement of public property."
    ),
    "lok_sabha": (
        ["lok sabha", "general election", "parliament", "mp election", "18th lok sabha"],
        "**Lok Sabha (Indian Parliament) — Lower House:**\n- Total seats: **543**\n- Last election: **18th Lok Sabha (April 19 – June 1, 2024)** — held in 7 phases\n- Results declared: **June 4, 2024**\n- Next Lok Sabha election: **Due by 2029**\n\n🏛️ Lok Sabha members are elected directly by voters. Each constituency elects one Member of Parliament (MP)."
    ),
    "vidhan_sabha": (
        ["vidhan sabha", "state election", "assembly election", "mla", "state assembly"],
        "**Vidhan Sabha (State Legislative Assembly):**\nEach Indian state has its own Vidhan Sabha (Legislative Assembly). Members (MLAs) are elected directly by voters in the state.\n\n**Recent/Upcoming State Elections:**\n- 🗳️ **West Bengal, Tamil Nadu, Kerala, Assam** — April 2026 (results: May 4, 2026)\n- 🗳️ **Bihar** — Nov 2025 (completed)\n- 🗳️ **Delhi** — Feb 5, 2025 (completed)\n\nAsk me about a specific state for detailed dates!"
    ),
    "disclaimer": (
        ["data source", "is this accurate", "official source", "eci website"],
        "**Data Source:**\nAll election data provided by VoteWise India is sourced from the **Election Commission of India (ECI)** at [eci.gov.in](https://eci.gov.in).\n\n⚠️ Always verify important dates and rules with the official ECI website or call the National Voter Helpline at **1950** before taking action."
    ),
}

def find_local_answer(message: str) -> Optional[str]:
    """Returns a pre-built local answer or None (triggering Gemini call)."""
    lower = message.lower()
    for _key, (keywords, answer) in LOCAL_ANSWERS.items():
        if any(kw in lower for kw in keywords):
            return answer
    return None


def check_eligibility(age: int, citizen: bool, state: str) -> Dict[str, Any]:
    """India-specific voter eligibility check."""
    eligible = True
    reasons = []
    next_steps = []

    if not citizen:
        eligible = False
        reasons.append("केवल भारतीय नागरिक मतदान कर सकते हैं। (Only Indian citizens can vote in Indian elections.)")

    if age < 18:
        eligible = False
        reasons.append(f"आप {age} वर्ष के हैं। भारत में मतदान के लिए न्यूनतम आयु 18 वर्ष है। (Minimum age is 18 years.)")

    if eligible:
        reasons.append("✅ You meet the basic age and citizenship requirements to vote in India.")
        next_steps.append("Check if your name is on the electoral roll at voters.eci.gov.in.")
        next_steps.append("If not registered, fill Form 6 online at voters.eci.gov.in.")
        next_steps.append("Download your e-EPIC (digital Voter ID) from the Voter Helpline App.")
    else:
        next_steps.append("Wait until you meet the eligibility criteria.")
        next_steps.append("Learn more about civic participation at eci.gov.in.")

    return {"eligible": eligible, "reasons": reasons, "next_steps": next_steps}


def get_deadlines(state: str) -> Dict[str, Any]:
    """Returns election schedule for a given Indian state code."""
    state_upper = state.upper()
    state_data = ELECTION_DATA.get("states", {}).get(state_upper)
    if not state_data:
        return {"error": f"No data found for state code: {state_upper}. Supported: DL, BR, WB, TN, KL, AS, UP, MH, GJ, RJ, KA, MP, PB"}
    return {
        "state_name": state_data.get("name"),
        "last_election_date": state_data.get("last_election_date"),
        "next_election_due": state_data.get("next_election_due"),
        "enrollment_deadline": state_data.get("enrollment_deadline"),
        "notes": state_data.get("notes"),
    }


def get_state_rules(state: str) -> Dict[str, Any]:
    """Returns voting rules for a given Indian state code."""
    state_upper = state.upper()
    state_data = ELECTION_DATA.get("states", {}).get(state_upper)
    if not state_data:
        return {"error": f"No data found for state code: {state_upper}"}
    return {
        "state_name": state_data.get("name"),
        "assembly": state_data.get("assembly"),
        "total_seats": state_data.get("total_seats"),
        "epic_required": state_data.get("epic_required"),
        "alternative_ids_accepted": ELECTION_DATA.get("alternative_id_documents", []),
        "official_url": state_data.get("official_url"),
        "eci_helpline": state_data.get("eci_helpline", "1950"),
    }
