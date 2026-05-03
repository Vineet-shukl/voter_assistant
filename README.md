<div align="center">

# 🗳️ VoteWise India

### *Your non-partisan AI guide to Indian elections*

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Firebase_Hosting-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://voterwise-c0186.web.app)
[![Firebase Functions](https://img.shields.io/badge/Firebase_Functions-Gen_2-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/docs/functions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-Google_AI-8E44AD?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-FF9933?style=for-the-badge)](LICENSE)

<br/>

> **Helping every Indian citizen** understand voter registration, eligibility, EPIC cards, EVM voting, and election schedules — powered by official Election Commission of India (ECI) data.

<br/>

![VoteWise India Preview](https://img.shields.io/badge/🇮🇳_Serving_India-ECI_Data_Powered-138808?style=for-the-badge)

</div>

---

## ✨ What is VoteWise India?

VoteWise India is a **conversational election assistant** built for Indian citizens. It combines a deterministic rules engine (grounded in real ECI data) with Google's Gemini AI to give fast, accurate, non-partisan answers to questions about the Indian election process.

Whether you're a first-time voter at 18 or someone who just moved cities and needs to update their registration — VoteWise speaks your language. Literally. **It natively supports all 22 official Indian languages** via instant UI translation and language-aware AI prompting.

---

## 🏗️ Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                   USER  (Browser / Mobile)                  │
│       Glassmorphism UI · 22 Languages · Quick Nav Bar       │
└──────────────────────────┬─────────────────────────────────┘
                           │  HTTPS
                           ▼
┌────────────────────────────────────────────────────────────┐
│             FIREBASE HOSTING (Global Edge CDN)              │
└──────────────────────────┬─────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│      FIREBASE FUNCTIONS (Gen 2 / Google Cloud Run)          │
│                                                             │
│   POST /chat ──► Layer 1: Partisan Guard    (instant)       │
│                      │                                      │
│                      ▼                                      │
│              Layer 2: Firestore Cache       (24h TTL)       │
│                      │                                      │
│                      ▼                                      │
│              Layer 3: Gemini 1.5 Flash      (Google AI)     │
│                                                             │
│   GET /eligibility ──► Deterministic eligibility check      │
│   GET /timeline    ──► State election schedule JSON         │
│   GET /states      ──► Supported state list                 │
│   GET /health      ──► Health probe                         │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────┐
│       FIRESTORE (Rate Limiting & Response Cache)            │
└────────────────────────────────────────────────────────────┘
```

### Three-Layer AI System

| Layer | Trigger | Speed | API Cost |
|---|---|---|---|
| 🛡️ **Partisan Guard** | Political party / candidate mentions | Instant | Zero |
| 🗂️ **Firestore Cache** | Repeated questions (24h TTL) | ~10ms | Zero |
| 🤖 **Gemini 1.5 Flash** | New, unique queries | ~1–2s | Minimal |

> **Repeated questions are served from Firestore cache — zero AI cost on cache hits.**

---

## 🔒 Security

- **Distributed Rate Limiting:** Per-user/IP rate limiting via atomic Firestore transactions (30 req/hr).
- **Locked-down Firestore Rules:** `allow read, write: if false` — no client SDK access.
- **Strict CORS & HTTP Headers:** CSP, HSTS, X-Frame-Options, Referrer-Policy locked to production domains.
- **Non-Partisan Guardrails:** Keyword blocking intercepts political party/candidate mentions before calling the LLM.
- **Firebase Secrets:** `GEMINI_API_KEY` stored as a Firebase Secret (never in code or env files).

---

## 🚀 CI/CD

Every push to `main` automatically deploys via **GitHub Actions**:

1. Checks out code
2. Sets up Python 3.11 & creates `functions/venv`
3. Installs dependencies (`google-generativeai`, `firebase-admin`, etc.)
4. Deploys Functions + Hosting to Firebase

**Required GitHub Secrets:**

| Secret | How to get it |
|---|---|
| `FIREBASE_TOKEN` | Run `firebase login:ci` locally |
| *(Firebase Secret)* `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → set via `npx firebase-tools functions:secrets:set GEMINI_API_KEY` |

---

## 🛠️ Local Setup

### Prerequisites
- Node.js 18+ and `npm install -g firebase-tools`
- Python 3.11+
- A Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 1. Clone & Install
```bash
git clone https://github.com/Vineet-shukl/voter_assistant.git
cd voter_assistant

cd functions
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Set the Gemini API Key (Firebase Secret)
```bash
npx firebase-tools functions:secrets:set GEMINI_API_KEY
# Paste your key when prompted
```

### 3. Deploy
```bash
npx firebase-tools deploy --only functions,hosting
```

---

## 📁 Project Structure

```text
voter_assistant/
│
├── .github/workflows/
│   └── deploy.yml           # GitHub Actions CI/CD pipeline
│
├── functions/               # Firebase Gen 2 Cloud Functions (Python 3.11)
│   ├── main.py              # Endpoints, CORS, Auth, Rate Limiting
│   ├── gemini_client.py     # Gemini API wrapper with Firestore caching
│   ├── rules_engine.py      # ECI data lookup + local deterministic answers
│   ├── prompts.py           # System prompt builder
│   ├── requirements.txt     # Python dependencies
│   └── data/
│       └── election_data.json # ECI election schedules
│
├── static/                  # Firebase Hosting Frontend
│   ├── index.html           # Chat UI (glassmorphism)
│   ├── style.css            # India tricolor design system
│   ├── app.js               # UI logic and API fetch layer
│   └── firebase-init.js     # Firebase SDK initialization
│
├── tests/                   # Pytest suite
│   ├── test_api.py
│   ├── test_rules.py
│   └── test_safety.py
│
├── firebase.json            # Firebase configuration
└── firestore.rules          # Locked-down security rules
```

---

## ♿ Accessibility & UI

- **22 Indian Languages** — instant UI translation + AI responds in chosen language
- `aria-live="polite"` on chat log for screen readers
- Full keyboard navigation (Tab + Enter)
- Mobile-optimized for screens down to 360px
- `prefers-reduced-motion` respected
- Semantic HTML (`<main>`, `<header>`, `<form>`, `<button>`)

---

## 📜 License

MIT © 2026 — Free to use, fork, & adapt for civic good.

---

<div align="center">

**Built with ❤️ for Indian democracy**

[🌐 Live Demo](https://voterwise-c0186.web.app) · [📞 ECI Helpline: 1950](tel:1950) · [🏛️ eci.gov.in](https://eci.gov.in)

*Data sourced from ECI. Always verify critical dates at [eci.gov.in](https://eci.gov.in) or call **1950** (toll-free).*

</div>
