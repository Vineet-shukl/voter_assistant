# 🗳️ VoteWise — Election Process Assistant

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)
![Cloud Run](https://img.shields.io/badge/Google_Cloud-Run-4285F4?logo=google-cloud)
![Gemini API](https://img.shields.io/badge/Google_AI-Gemini-8E75B2?logo=google)

VoteWise is a conversational web assistant that helps first-time and confused voters understand the election process—from checking eligibility, registering, knowing deadlines, finding polling locations, to understanding what happens on election day.

## 🎯 Chosen Vertical
**Civic Engagement / Election Awareness**
Designed for "Alex" — the first-time voter who prefers conversational interfaces over dense government PDFs.

## 💡 Approach & Logic
VoteWise uses a **Hybrid Rules + LLM architecture**:
- **Rules Engine (Deterministic):** Handles eligibility logic, deadlines, and state requirements. This prevents hallucination of critical civic information.
- **Gemini 2.5 Flash (LLM):** Handles conversation, natural language summarization, and explanation based on the grounded context from the rules engine.

## 🏗️ How It Works
1. **User asks a question** via the chat interface.
2. The **FastAPI backend** receives the message and any contextual data (e.g., age, state).
3. The backend calls the **Rules Engine** to retrieve any structured information needed (deadlines, eligibility).
4. A **grounded prompt** is built, combining system instructions, user input, and facts from the Rules Engine.
5. **Gemini API** generates a natural, non-partisan reply.
6. The response is sent back and rendered in the **Accessible Chat UI**.

## ⚙️ Google Services Used
- **Google Cloud Run:** Serverless container hosting
- **Google Cloud Build:** Auto-builds the Docker image from source
- **Google Artifact Registry:** Stores the container image
- **Google Gemini API:** Conversational AI (gemini-2.5-flash)

## 🚀 Live Demo URL
**[https://votewise-48563985294.us-central1.run.app](https://votewise-48563985294.us-central1.run.app)**

## 🧪 Testing
The project includes a robust suite of unit and integration tests (built with `pytest`).
```bash
python -m pytest -v
```

## ♿ Accessibility Features
- Mobile-first, responsive design (max-width 720px)
- High-contrast toggle switch
- WCAG-AA compliant colors
- Full keyboard navigation and visible focus rings
- ARIA live regions for chat announcements

## 🔒 Security Measures
- **No PII storage:** The application is entirely stateless.
- **Strict Prompting:** Gemini is instructed to refuse partisan queries or candidate endorsements.
- **Environment Variables:** Secrets are never committed to version control.

## 📌 Assumptions & Limitations
- **Data:** State rules and deadlines provided in `election_data.json` are *illustrative examples* for the hackathon and not real-time legal advice.
- **Authentication:** For the hackathon, the app is deployed allowing unauthenticated access. Rate limiting is assumed to be handled at the Cloud Run/Cloud Armor layer in a production scenario.

## 🛠️ Local Setup
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd votewise-election-assistant
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set your Gemini API key in a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```
5. Open `http://localhost:8080` in your browser.

## 📜 License
MIT License