# 🧠 FINAL AI AGENT INSTRUCTION

## Project: Finance Market Brief + AI Podcast Generator

Backend: Python + FastAPI
Frontend: ReactJS
LLM Integration: Google Gemini 2.x (via Google ADK)
Podcast: Sarvam AI TTS (for natural Hinglish)

---

# 🎯 SYSTEM OBJECTIVE

Build a production-ready, fully automated system where:

1. User enters a finance topic (or leaves blank for a complete global + India market update).
2. LLM acts as a Finance Research Agent — it does not rely on memory or training data.
3. Agent autonomously identifies, scrapes, and validates authoritative financial sources.
4. Fetches ONLY yesterday's verified closing data:
   * 🌍 Global market updates — US, Europe, Asia, commodities, macro
   * 🇮🇳 India-specific updates — indices, RBI, FII/DII, earnings, government news
5. Extracts factual numeric data only — no estimates, no approximations.
6. Generates a professional 2–4 minute natural-speech podcast script.
7. Converts script to MP3 via ElevenLabs TTS.
8. Returns a structured JSON response with summaries + audio URL.
9. React frontend displays the full summary, key takeaway, and an interactive audio player.

---

# 🚨 HARD CONSTRAINTS

These rules are absolute. The LLM must never deviate from them under any circumstance.

* **Only use yesterday's verified, published data.** The date must be confirmed from article metadata — not assumed.
* **Never hallucinate numbers.** Every figure must exist verbatim in the scraped source text.
* **Never use training memory for market data.** Even if the LLM believes it knows a closing price, it must not use it.
* **Never include today's live or real-time data.** Yesterday's closing data is the only valid input.
* **Never fabricate missing information.** If data is not found, output exactly: `"Insufficient verified updates for yesterday."`
* **Exclude opinion-heavy blogs, social media, forums, and unverified aggregators.**
* **Return structured output only.** No prose, explanation, or commentary outside the defined JSON fields.
* **Enforce the date filter twice** — once during scraping (metadata check) and once during LLM analysis (content validation).

---

# 📊 DATA PRIORITY RULES

## 🌍 Global Markets — Cover First, In This Order

Extract closing values, points change, and percentage change for each metric where available:

* **US Indices** — S&P 500, Nasdaq Composite, Dow Jones Industrial Average
* **European Markets** — FTSE 100 (UK), DAX (Germany), CAC 40 (France)
* **Asian Markets** — Nikkei 225 (Japan), Hang Seng (Hong Kong), KOSPI (South Korea)
* **Oil** — Brent Crude settlement price per barrel + percentage change
* **Gold** — Spot price per troy ounce + percentage change
* **USD Index** — DXY level + directional move
* **Federal Reserve** — Any rate decision, official speech, or forward guidance published yesterday
* **Major Macro Releases** — CPI, NFP, GDP, or any other significant economic data released yesterday

---

## 🇮🇳 India Markets — Mandatory, Never Skip

All of the following must be included. If data is unavailable, state it explicitly — do not omit the field silently:

* **Nifty 50** — Closing level + points change + percentage change + session high and low if available
* **Sensex (BSE)** — Closing level + points change + percentage change
* **RBI** — Any rate decision, liquidity measure, policy statement, or official communication published yesterday
* **INR Movement** — USD/INR spot rate + daily change direction (strengthened or weakened)
* **FII Activity** — Net buy or net sell figure in crore INR for yesterday's session
* **DII Activity** — Net buy or net sell figure in crore INR for yesterday's session
* **Major Corporate Earnings** — Any Nifty 50 or large-cap company quarterly result announced yesterday, with net profit and YoY comparison
* **Government Announcements** — Budget updates, infrastructure spending, tax policy, or regulatory changes published yesterday

---

# 🏗️ COMPLETE PROJECT STRUCTURE

```
finance-ai-podcast/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logger.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes_generate.py
│   │   │
│   │   ├── services/
│   │   │   ├── orchestrator_service.py
│   │   │   ├── unified_agent_service.py
│   │   │   ├── podcast_service.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── request_schema.py
│   │   │   ├── response_schema.py
│   │   │
│   │   ├── storage/
│   │   │   ├── audio/
│   │   │   ├── raw_data/
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   ├── apiClient.js
│   │   │
│   │   ├── components/
│   │   │   ├── TopicInput.jsx
│   │   │   ├── SummaryDisplay.jsx
│   │   │   ├── AudioPlayer.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │
│   │   ├── App.js
│   │   ├── index.js
│   │
│   ├── package.json
│   └── .env
│
└── README.md
```

---

# 🔎 BACKEND SERVICE RESPONSIBILITIES

Each service has a single, clearly defined responsibility. No service should perform tasks that belong to another.

---

## 1️⃣ orchestrator_service.py

**Role: Central Pipeline Controller**

This is the master coordinator. It does not perform any scraping, filtering, or analysis itself — it sequences and triggers all other services in the correct order and ensures data flows correctly between them.

Responsibilities:
* Inject yesterday's date into the process
* Trigger the **UnifiedAgentService** for end-to-end Research, Analysis, and Script generation
* Pass the final script to the **PodcastService** for audio conversion
* Assemble and return the complete final JSON response
* Save raw generated data to `storage/raw_data/` for audit and debugging purposes
* Handle failures gracefully

---

## 2️⃣ unified_agent_service.py

**Role: Unified Research & Analysis Agent (Google ADK)**

This service leverages Google's Agent Development Kit (ADK) to perform an integrated pipeline in a single conceptual "agent run", although it internally manages search and analysis.

Responsibilities:
* **Autonomous Research**: Uses the native `google_search` tool to find the LATEST verified market closing data.
* **Date-Locked Scoping**: Explicitly searches for and validates data specifically for the target date.
* **Intelligent Analysis**: Analyzes gathered data to identify key facts, trends, and connections between Indian and global markets.
* **Hinglish Scripting**: Generates a high-quality narrative podcast script in Hinglish (Roman script), optimized for TTS with pauses and natural flow.
* **Structured Output**: Returns a robust JSON containing analysis, script, sources, and data quality metrics.

---

## 3️⃣ podcast_service.py

**Role: Sarvam AI TTS Audio Converter**

Responsibilities:
* Sends the finalized Hinglish script to the Sarvam AI API.
* Uses the `hi-IN` target language with natural voices (e.g., "anushka") ideal for Hinglish content.
* Automatically locates `ffmpeg` on the system and configures `pydub` for conversion.
* Converts raw audio (WAV) to high-quality MP3 (192k bitrate).
* Saves the returned audio in `storage/audio/`.
* Serve the file via the `/audio/{filename}` static mount and return the public URL.

---

# 💻 FRONTEND (ReactJS)

## Responsibilities

* Provide a clean, minimal topic input interface
* Call the backend `/generate` endpoint with the user's topic on submit
* Display a loading state while the pipeline runs (it may take 20–40 seconds)
* Render the structured response clearly:
  * Global market summary
  * India market summary
  * Key takeaway
  * Interactive audio player if audio_url is present
  * Script viewer (optional expandable section)
* Handle errors gracefully with a user-facing message

---

## Component Breakdown

### TopicInput.jsx
* Controlled text input bound to local state
* Submit button that triggers the API call
* Visual loading indicator while awaiting response
* Optional quick-select chips for common topics (e.g. "RBI Policy", "FII Activity", "Nifty Analysis")
* Clears and resets cleanly after each submission

### SummaryDisplay.jsx
* Renders three clearly separated sections: Global Markets, Indian Markets, Key Takeaway
* Each section has a distinct visual heading and formatted paragraph body
* Handles the case where a section returns "Insufficient verified updates for yesterday." gracefully
* Shows source URLs used, collapsed by default

### AudioPlayer.jsx
* Renders a native `<audio controls src={audio_url} />` element
* Includes a download link for the MP3
* Only renders if `audio_url` is present in the response — does not render a broken player on null

### apiClient.js
* Axios or fetch wrapper with a base URL pulled from environment variable `REACT_APP_API_URL`
* Single `generate(topic)` function that posts to `/api/v1/generate`
* Handles HTTP errors and network failures and returns a structured error object to the calling component

---

# ⚙️ TECH STACK REQUIREMENTS

## 🔹 Backend

* Python 3.10+
* FastAPI — async REST API framework
* Google ADK — for autonomous agent capabilities and Google Search tool
* Pydantic v2 — schema validation
* python-dotenv — environment variable management
* pydub — for audio format conversion (WAV to MP3)
* ffmpeg — system dependency for audio processing

**requirements.txt must include:**
```
fastapi
uvicorn[standard]
httpx
requests
python-dotenv
pydantic
aiofiles
python-multipart
pydantic-settings
google-adk
google-adk-tools
pydub
```

---

## 🔹 Frontend

* React 18+ with functional components and hooks only — no class components
* Axios for API communication
* Environment variable support via `.env` and `REACT_APP_` prefix
* CSS Modules or Tailwind CSS for styling
* No external state management library required — useState and useEffect are sufficient

---

## 🔹 DevOps (Recommended)

* Docker for backend containerisation
* Docker Compose for local full-stack development
* Nginx as reverse proxy in production — serves frontend static files and proxies `/api` to FastAPI
* CI/CD pipeline — GitHub Actions or equivalent for automated build and test on push
* Structured logging with timestamps and service-level labels for observability
* Rate limiting on the `/generate` endpoint — recommended: 5 requests per minute per IP
* CORS configuration — restrict allowed origins to the frontend domain in production

---

# 📦 FINAL API RESPONSE FORMAT

The `/api/v1/generate` endpoint must return exactly this structure. All fields are always present. Use `null` for optional fields that could not be populated.

```json
{
  "date": "YYYY-MM-DD",
  "topic": "user topic or null",
  "data_summary": "High-level summary of found data",
  "overview": "Main narrative summary and key takeaways",
  "india_analysis": "Detailed India-focused technical analysis",
  "global_analysis": "Detailed Global-focused technical analysis",
  "insights": "Connections, risks, and opportunities",
  "podcast_script": "Full Hinglish narrative script",
  "audio_url": "http://host/audio/filename.mp3",
  "sources_used": ["url1", "url2"],
  "data_quality": "High/Medium/Low",
  "status": "success",
  "error": null
}
```

---

# 🔥 FINAL AGENT BEHAVIOR EXPECTATION

The LLM must operate exactly like a disciplined financial analyst producing a live broadcast briefing. Internalize these principles:

* **Global first, always** — never lead with India data before covering global markets
* **Numbers are sacred** — every figure in the output must be traceable to a scraped source from yesterday
* **Silence over fabrication** — "Insufficient verified updates for yesterday." is always better than an invented number
* **Date discipline** — if an article does not carry a clear yesterday timestamp, its data is inadmissible
* **Neutral voice** — the tone is a Bloomberg anchor, not a financial blogger
* **Clean output** — the JSON must be machine-parseable with no extra text, markdown, or commentary outside the defined fields
* **Graceful degradation** — a partial response with honest gaps is far better than a complete response with fabricated data

---
