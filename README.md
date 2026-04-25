<div align="center">

# 🗳️ VoteWise India

### *Your non-partisan AI guide to Indian elections*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Cloud_Run-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://votewise-48563985294.us-central1.run.app)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-8E44AD?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-FF9933?style=for-the-badge)](LICENSE)

<br/>

> **Helping every Indian citizen** understand voter registration, eligibility, EPIC cards, EVM voting, and election schedules — powered by official Election Commission of India (ECI) data.

<br/>

![VoteWise India Preview](https://img.shields.io/badge/🇮🇳_Serving_India-ECI_Data_Powered-138808?style=for-the-badge)

</div>

---

## ✨ What is VoteWise India?

VoteWise India is a **conversational election assistant** built for Indian citizens. It combines a deterministic rules engine (grounded in real ECI data) with Google's Gemini AI to give fast, accurate, non-partisan answers to questions about the Indian election process.

Whether you're a first-time voter at 18 or someone who just moved cities and needs to update their registration — VoteWise speaks your language.

```
User  ❯  "I forgot to register. Can I still vote?"
Bot   ❯  ✅ Yes! ECI runs quarterly revisions (Jan, Apr, Jul, Oct).
          File Form 6 at voters.eci.gov.in — your name will be added
          after the next revision cycle. Helpline: 1950 (toll-free).
```

---

## 🎯 Vertical: Civic Engagement

| | |
|---|---|
| **Problem** | Millions of eligible Indian voters miss elections due to confusion about registration, ID requirements, and deadlines |
| **Solution** | A 24×7 conversational assistant that gives instant, accurate, non-partisan guidance — in plain language |
| **Impact** | Reduces dependency on dense government PDFs; increases voter participation |
| **Data Source** | Election Commission of India — [eci.gov.in](https://eci.gov.in) |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   USER  (Browser / Mobile)                  │
│          Glassmorphism Chat UI · HTML · CSS · JS            │
└──────────────────────────┬─────────────────────────────────┘
                           │  HTTPS
                           ▼
┌────────────────────────────────────────────────────────────┐
│              GOOGLE CLOUD RUN  (FastAPI · Python 3.11)      │
│                                                             │
│   POST /chat ──► Layer 1: Local Keyword Match  (0 tokens)   │
│                      │                                      │
│                      ▼ (if no match)                        │
│              Layer 2: Rules Engine  (structured ECI data)   │
│                      │                                      │
│                      ▼ (complex / state-specific only)      │
│              Layer 3: Gemini 2.5 Flash Lite  (AI reply)     │
│                                                             │
│   GET /eligibility ──► Deterministic eligibility check      │
│   GET /timeline    ──► State election schedule JSON         │
│   GET /states      ──► Supported state list                 │
│   GET /health      ──► Liveness probe                       │
└────────────────────────────────────────────────────────────┘
```

### Three-Layer Answer System

| Layer | Trigger | Speed | API Cost |
|---|---|---|---|
| ⚡ **Local Keywords** | 17 built-in topics (EPIC, EVM, Form 6…) | Instant | Zero |
| 🗂️ **Rules Engine** | State-specific data enrichment | ~1ms | Zero |
| 🤖 **Gemini AI** | Complex / unique queries only | ~1–2s | Minimal |

> **~80% of common questions are answered locally — no API call made.**

---

## 🚀 Live Demo

**➜ [https://votewise-48563985294.us-central1.run.app](https://votewise-48563985294.us-central1.run.app)**

Try asking:
- *"How do I register to vote in India?"*
- *"What alternative IDs are accepted at the polling booth?"*
- *"I am unable to vote — what are the reasons?"*
- *"What is VVPAT and how does EVM work?"*
- *"When is the next West Bengal election?"*
- *"I moved to Delhi. How do I update my address?"*

---

## ⚙️ Google Services Used

| Service | Role |
|---|---|
| **Google Cloud Run** | Serverless container hosting (auto-scales to zero) |
| **Google Cloud Build** | Automated container image build from source |
| **Google Artifact Registry** | Stores and serves the container image |
| **Google Gemini API** | Conversational AI for complex voter queries |

---

## 💡 How It Works

### 1. Non-Partisan Safety Guard
Every message is scanned for partisan keywords (party names, candidate names) before reaching the AI. Matching messages get a firm, polite refusal — no API call made.

### 2. Local Answer Layer (17 Topics — Zero Tokens)
Built-in, ECI-accurate answers for the most common voter questions:

| Topic | Keywords caught |
|---|---|
| Voter Registration | form 6, forgot to register, enroll, still register… |
| EPIC / Voter ID | voter id, epic card, e-epic, matdata pehchan… |
| Alternative IDs | aadhaar to vote, no voter id, 12 documents… |
| EVM & VVPAT | evm, electronic voting machine, how to vote… |
| Unable to Vote | cannot vote, unable to vote, classify reason… |
| Electoral Roll | name not found, am i registered, naam nahi hai… |
| Address Change | moved house, new city, pata badal gaya… |
| cVIGIL App | report violation, mcc violation, bribery… |
| Model Code | model code of conduct, adarsh achaar… |
| + 8 more | Lok Sabha, Vidhan Sabha, ECI contact, NRI voting… |

### 3. Rules Engine (Deterministic, Hallucination-Free)
Election dates, state schedules, and eligibility rules come from a structured JSON file sourced from ECI — **never generated by the AI**. Gemini only sees this data after it's been validated by the rules engine.

### 4. Gemini AI (Last Resort, Token-Efficient)
- Model: `gemini-2.5-flash-lite` (primary) → `gemini-2.5-flash` (fallback)
- Temperature: 0.2 (deterministic, factual)
- Max output: 512 tokens (cost-capped)
- Session cache: 10-minute client-side cache prevents duplicate API calls

---

## 🗺️ Supported States & Election Data

| State | Last Election | Next Due |
|---|---|---|
| West Bengal | Apr 29, 2026 | 2031 |
| Tamil Nadu | Apr 23, 2026 | 2031 |
| Kerala | Apr 9, 2026 | 2031 |
| Assam | Apr 9, 2026 | 2031 |
| Bihar | Nov 11, 2025 | 2030 |
| Delhi | Feb 5, 2025 | 2030 |
| Uttar Pradesh | 2022 | 2027 |
| Gujarat | 2022 | 2027 |
| Punjab | 2022 | 2027 |
| Maharashtra | Nov 20, 2024 | 2029 |
| Karnataka | May 10, 2023 | 2028 |
| Rajasthan | Nov 25, 2023 | 2028 |
| Madhya Pradesh | Nov 17, 2023 | 2028 |

*Data sourced from ECI. Always verify at [eci.gov.in](https://eci.gov.in) or call **1950**.*

---

## 🛠️ Local Setup

### Prerequisites
- Python 3.11+
- A Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/voter_assistant.git
cd voter_assistant

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and set: GEMINI_API_KEY=your_key_here

# 5. Run the app
uvicorn app.main:app --reload --port 8080

# 6. Open in browser
# http://localhost:8080
```

### Run Tests
```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
voter_assistant/
│
├── app/
│   ├── main.py              # FastAPI routes & 3-layer answer logic
│   ├── gemini_client.py     # google-genai SDK wrapper (2.5-flash-lite)
│   ├── rules_engine.py      # ECI data lookup + 17 local answer topics
│   ├── prompts.py           # System prompt builder (token-efficient)
│   ├── models.py            # Pydantic request/response schemas
│   └── data/
│       └── election_data.json  # ECI election schedules (13 states/UTs)
│
├── static/
│   ├── index.html           # Chat UI (glassmorphism, dark/light mode)
│   ├── style.css            # India tricolor design system
│   └── app.js               # Session cache, debounce, fetch logic
│
├── tests/
│   ├── test_rules.py        # Rules engine unit tests
│   ├── test_api.py          # API endpoint integration tests
│   └── test_safety.py       # Partisan refusal tests
│
├── Dockerfile               # python:3.11-slim, port 8080
├── requirements.txt         # Pinned dependencies
└── .env.example             # API key template (never commit .env)
```

---

## 🔒 Security & Privacy

| Measure | Status |
|---|---|
| No API key in code or Git history | ✅ |
| API key injected via Cloud Run env var | ✅ |
| Input validation via Pydantic (max 500 chars) | ✅ |
| Zero PII storage — fully stateless backend | ✅ |
| Client-side session storage only (cleared on tab close) | ✅ |
| Non-partisan AI guardrails (party names blocked) | ✅ |
| HTTPS enforced by Cloud Run | ✅ |
| Container runs as non-root | ✅ |

---

## ♿ Accessibility

- `aria-live="polite"` on chat log for screen readers
- Full keyboard navigation (Tab + Enter)
- `prefers-reduced-motion` media query respected
- WCAG AA colour contrast ratios
- Semantic HTML (`<main>`, `<header>`, `<form>`, `<button>`)
- Mobile-first responsive layout

---

## 📜 License

MIT © 2026 — Free to use, fork, and adapt for civic good.

---

<div align="center">

**Built with ❤️ for Indian democracy**

[🌐 Live Demo](https://votewise-48563985294.us-central1.run.app) · [📞 ECI Helpline: 1950](tel:1950) · [🏛️ eci.gov.in](https://eci.gov.in)

*Data is sourced from ECI and is illustrative. Always verify critical dates and rules at [eci.gov.in](https://eci.gov.in) or by calling the National Voter Helpline at **1950** (toll-free).*

</div>