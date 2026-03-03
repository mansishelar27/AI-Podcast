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
│   │   ├── schemas/
│   │   │   ├── request_schema.py
│   │   │   ├── response_schema.py
│   │   │
│   │   ├── services/
│   │   │   ├── orchestrator_service.py
│   │   │   ├── news_service.py
│   │   │   ├── unified_agent/
│   │   │   │   ├── agent_init.py
│   │   │   │   ├── prompt_builder.py
│   │   │   │   ├── service.py
│   │   │   ├── podcast/
│   │   │   │   ├── service.py
│   │   │   │   ├── script_splitting.py
│   │   │   │   ├── audio.py
│   │   │
│   │   ├── storage/
│   │   │   ├── audio/
│   │   │   ├── raw_data/
│   │
│   ├── requirements.txt
│   ├── .env
│   └── venv/
│
├── frontend/
│   └── frontend/
│       ├── public/
│       ├── src/
│       │   ├── api/
│       │   │   ├── apiClient.js
│       │   ├── components/
│       │   │   ├── TopicInput.jsx
│       │   │   ├── SummaryDisplay.jsx
│       │   │   ├── AudioPlayer.jsx
│       │   ├── pages/
│       │   │   ├── Home.jsx
│       │   ├── App.js
│       │   ├── index.js
│       ├── package.json
│       └── .env
│
└── README.md
```

---

# 🔎 BACKEND SERVICE RESPONSIBILITIES

Each service has a single, clearly defined responsibility. No service should perform tasks that belong to another.

---

## 1️⃣ orchestrator_service.py

**Role: Central Podcast Pipeline Controller**

This is the master coordinator. It does not perform any web scraping or LLM work itself — it sequences and triggers the unified agent and podcast services in the correct order and ensures data flows correctly between them.

Responsibilities:
* Inject yesterday's date into the process
* Trigger the **UnifiedAgentService** for end-to-end research and bilingual script generation (English + Hindi)
* Split long scripts into smaller chunks for Sarvam TTS
* Call **PodcastService** to generate audio in English, Hindi, or both depending on the `language` parameter
* Assemble and return the final JSON response (matching `GenerateResponse`)
* Save raw generated data to `storage/raw_data/` for audit and debugging purposes
* Handle failures and invalid inputs gracefully and return standardized error payloads

---

## 2️⃣ unified_agent (Google ADK)

**Role: Unified Research & Script Agent (Google ADK)**

This package (`app/services/unified_agent/`) leverages Google's Agent Development Kit (ADK) plus the `google_search` tool to perform an integrated pipeline in a single conceptual "agent run".

Responsibilities:
* **Autonomous Research**: Uses the native `google_search` tool to find the latest relevant financial news and macro updates around the target date.
* **Date-Aware Scoping**: Searches specifically for financial news around the requested date (usually yesterday).
* **English + Hindi Scripts**: Generates a complete English script and a corresponding Hindi script using a fixed output format with `=====ENGLISH PODCAST SCRIPT=====` and `=====HINDI PODCAST SCRIPT=====` markers.
* **Cleaning & Validation**: Cleans the raw LLM output, enforces minimum length for both scripts, and returns a structured dict (`eng_pod`, `hin_pod`, `sources_used`, metadata).

---

## 3️⃣ podcast (Sarvam TTS integration)

**Role: Sarvam AI TTS Audio Converter**

This package (`app/services/podcast/`) is responsible for turning the generated scripts into MP3 audio using Sarvam AI.

Responsibilities:
* Wrap Sarvam AI `text-to-speech` endpoint with sane defaults and logging
* Provide a high-level `PodcastService` that can:
  * Generate audio for a **single** script (legacy mode)
  * Generate audio for **both** English and Hindi scripts together
* Use voices such as `"sachit"` (English) and `"anushka"` / `"karan"` (Hindi), configurable per request
* Save audio files under `storage/audio/` with timestamped filenames
* Return relative URLs like `/audio/podcast_hi_YYYYMMDD_HHMMSS.mp3` that FastAPI serves via `StaticFiles`

---

## 4️⃣ news_service.py

**Role: Financial News Aggregator**

Responsibilities:
* Fetch and aggregate financial / stock market news from multiple India-focused RSS feeds
* Normalize items into a common shape: title, link, published date, snippet, and source
* Deduplicate similar stories by title and sort by published date (newest first)
* Power the `/financial-news` endpoint used by the frontend "Market & financial news" sidebar

---

## 5️⃣ FastAPI application (main.py)

**Role: API Composition Layer**

Responsibilities:
* Configure CORS and load settings from environment using `pydantic-settings`
* Create storage directories (`storage/audio`, `storage/raw_data`) at startup
* Mount static `/audio` for serving generated MP3s
* Include all routes from `app/api/routes_generate.py` under `/api/v1`
* Expose a simple health/welcome endpoint at `/`

---

## 6️⃣ Core configuration & logging

* `core/config.py` – central `Settings` object with:
  * `PROJECT_NAME`, `API_V1_STR`
  * `GEMINI_API_KEY`, `SARVAM_API_KEY`
  * `GEMINI_MODEL` (e.g., `gemini-2.5-flash`)
  * `AUDIO_STORAGE_PATH`, `RAW_DATA_STORAGE_PATH`
* `core/logger.py` – process-wide logger configured to stdout with timestamps and service labels

---

## 7️⃣ Backend API endpoints

All backend endpoints are mounted under `settings.API_V1_STR` (default: `/api/v1`):

* `GET /api/v1/agent-info`  
  * Returns `{ "description": AGENT_DESCRIPTION }` so the frontend can display "Agent description".
* `GET /api/v1/agent-instruction?date=YYYY-MM-DD&attribution=Smart+Finance+Agent`  
  * Returns `{ "instruction": "<full prompt>" }` built by `prompt_builder.build_podcast_prompt`.
* `GET /api/v1/financial-news?limit=25`  
  * Returns `{ "items": [...], "count": N }` news items for the homepage sidebar.
* `POST /api/v1/generate`  
  * Request body: `GenerateRequest` (see schemas below)  
  * Response body: `GenerateResponse` on success or a structured error JSON on failure.

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
* Pydantic v2 + `pydantic-settings` — validation and config
* `python-dotenv` — environment variable management
* `httpx` / `requests` — HTTP clients (Gemini, RSS feeds, Sarvam)
* `pydub` + `ffmpeg` — audio processing (WAV/MP3 conversion)
* `num2words` — for converting numbers to Hindi words in scripts

**Backend `requirements.txt` (simplified):**
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
httpx>=0.26.0
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
aiofiles>=23.2.0
python-multipart>=0.0.6
google-adk
pydub>=0.25.1
num2words>=0.5.13
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

The `/api/v1/generate` endpoint returns a JSON body that matches the `GenerateResponse` Pydantic model. A typical **success** response looks like this:

```json
{
  "status": "success",
  "date": "2026-02-26",
  "name": "Smart Finance Agent",
  "attribution": "Smart Finance Agent",
  "language": "en",
  "scripts": {
    "eng_pod": "Welcome to the Smart Finance Agent Financial Podcast. Today's edition: 2026-02-26...",
    "hin_pod": "स्मार्ट फाइनेंस एजेंट वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: 2026-02-26..."
  },
  "script_lengths": {
    "eng_pod": 1500,
    "hin_pod": 1600,
    "total": 3100
  },
  "audio": {
    "eng_pod_audio": "/audio/podcast_en_20260226_120000.mp3",
    "hin_pod_audio": null
  },
  "speaker": "sachit",
  "chunks": {
    "eng_pod_count": 3,
    "hin_pod_count": 3,
    "total": 6
  },
  "error": null,
  "sources_used": [
    "https://example.com/news-1",
    "https://example.com/news-2"
  ],
  "timestamp": "2026-02-26T12:00:00"
}
```

On **error**, the backend returns a consistent error shape (either directly from the route or via the `ErrorResponse` model), including at minimum:

```json
{
  "status": "error",
  "date": "2026-02-26",
  "name": "Smart Finance Agent",
  "language": "en",
  "scripts": null,
  "audio": null,
  "error": "Human-readable error message",
  "timestamp": "2026-02-26T12:00:00"
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
