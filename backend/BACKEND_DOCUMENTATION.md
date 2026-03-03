## Backend Documentation — Finance AI Podcast

### Overview

The backend is a **FastAPI** application that:

- **Generates bilingual podcast scripts** (English + Hindi) for daily financial briefings using **Google Gemini via Google ADK**.
- **Converts scripts to MP3 audio** using **Sarvam AI Text-to-Speech**.
- **Serves audio files** over HTTP and exposes **supporting metadata and news endpoints** for the React frontend.

The root package is `app/` with clear separation between API routes, configuration, services, and schemas.

---

### Project Layout (backend)

- `app/main.py`  
  - FastAPI app factory, CORS, static `/audio` mount, route inclusion.

- `app/core/config.py`  
  - `Settings` via `pydantic-settings`. Important fields:
    - `PROJECT_NAME`, `API_V1_STR` (default `/api/v1`)
    - `GEMINI_API_KEY`, `SARVAM_API_KEY`
    - `GEMINI_MODEL` (e.g. `gemini-2.5-flash`)
    - `AUDIO_STORAGE_PATH` (`storage/audio`)
    - `RAW_DATA_STORAGE_PATH` (`storage/raw_data`)

- `app/core/logger.py`  
  - Process-wide logger (`finance_ai_podcast`) configured to log to stdout.

- `app/api/routes_generate.py`  
  - All public HTTP endpoints used by the frontend:
    - `GET /agent-info`
    - `GET /agent-instruction`
    - `GET /financial-news`
    - `POST /generate`

- `app/schemas/request_schema.py`  
  - `GenerateRequest` (request body for `/generate`).

- `app/schemas/response_schema.py`  
  - `GenerateResponse`, `ErrorResponse` and helper models for response shape.

- `app/services/orchestrator_service.py`  
  - Orchestrates the full pipeline: invokes the unified agent, splits scripts, calls podcast service, composes final JSON.

- `app/services/unified_agent/`  
  - `agent_init.py` — initializes Google ADK `Agent` and `InMemorySessionService`.
  - `prompt_builder.py` — builds the **full prompt** for script generation given a `target_date` and `attribution`.
  - `service.py` — `UnifiedAgentService` that:
    - Calls the agent with the built prompt.
    - Parses and cleans the LLM output into `eng_pod` and `hin_pod`.
    - Returns metadata plus `sources_used`.

- `app/services/podcast/`  
  - `service.py` — `PodcastService` wrapper around audio generation.
  - `audio.py`, `script_splitting.py`, `file_utils.py`, `ffmpeg_check.py` — helpers for chunking, saving, and encoding audio.

- `app/services/news_service.py`  
  - Aggregates RSS feeds into a unified financial news list.

- `storage/audio/`  
  - Generated `.mp3` files, served as `/audio/{filename}` by FastAPI.

- `storage/raw_data/`  
  - Raw JSON dumps from the agent for auditing and debugging.

---

### Environment Configuration

Backend uses `.env` in the `backend/` directory. Required keys:

- `GEMINI_API_KEY` — Google Gemini API key (for Google ADK).  
  - Obtain from Google AI Studio and keep **secret**.
- `SARVAM_API_KEY` — Sarvam AI Text-to-Speech API key.  
  - Used for all TTS calls.

You must **never commit real API keys** to version control. In production, prefer environment variables or a secrets manager.

---

### Dependencies & Setup

Backend dependencies are in `requirements.txt` and include:

- `fastapi`, `uvicorn[standard]` — web framework and ASGI server.
- `httpx`, `requests` — HTTP clients (RSS, Gemini, Sarvam).
- `python-dotenv`, `pydantic`, `pydantic-settings` — config and validation.
- `aiofiles`, `python-multipart` — async file and form handling.
- `google-adk` — Agent framework used to drive Gemini.
- `pydub`, `ffmpeg` — audio processing (ensure `ffmpeg` is installed on the system PATH).
- `num2words` — numeric to words (Hindi) for TTS-friendly scripts.

**Local setup (recommended):**

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # on Windows
pip install -r requirements.txt

# Copy .env.example -> .env and fill GEMINI_API_KEY / SARVAM_API_KEY if an example file exists,
# otherwise create .env manually with those keys.
```

To run the API locally:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### API Endpoints

All endpoints are mounted under `settings.API_V1_STR` (default: `/api/v1`).

#### `GET /api/v1/agent-info`

- **Purpose**: Allow the frontend to display an "Agent description" string without duplicating it.
- **Response**:
  - `200 OK` with JSON:
    - `{ "description": "<AGENT_DESCRIPTION from agent_init.py>" }`

#### `GET /api/v1/agent-instruction`

- **Query params**:
  - `date` (`string`, default `"yesterday"`) — target date for financial updates.
  - `attribution` (`string`, default `"Smart Finance Agent"`) — brand/name used inside scripts.
- **Purpose**: Returns the **full prompt** built by `prompt_builder.build_podcast_prompt`.
- **Response**:
  - `200 OK`, `{ "instruction": "<full prompt string>" }`.

#### `GET /api/v1/financial-news`

- **Query params**:
  - `limit` (`int`, default `25`, max `50`) — number of items to return.
- **Purpose**: Provides aggregated finance/market news for the frontend sidebar.
- **Response**:
  - `200 OK` with:
    - `items`: list of `{ title, link, published, snippet, source }`
    - `count`: number of items returned.

#### `POST /api/v1/generate`

- **Body**: `GenerateRequest`

```json
{
  "name": "Smart Finance Agent",
  "voice_agent": "sachit",
  "language": "en",
  "custom_prompt": null
}
```

- **Fields**:
  - `name` (required) — podcast name / attribution.
  - `voice_agent` (optional) — specific TTS voice (e.g. `"sachit"`, `"anushka"`, `"karan"`).
  - `language` (enum: `"en"`, `"hi"`, `"both"`, default `"both"`) — which audio track(s) to generate.
  - `custom_prompt` (optional) — overrides default agent prompt for this single request if provided.

- **Success (200)**: `GenerateResponse`
  - Includes:
    - `status`: `"success"`.
    - `date`, `name`, `attribution`, `language`.
    - `scripts.eng_pod` and `scripts.hin_pod` (Hindi script with numbers converted to words for readability).
    - `script_lengths`, `chunks` (chunk counts), `speaker`.
    - `audio.eng_pod_audio` / `audio.hin_pod_audio` with relative URLs (e.g., `/audio/podcast_hi_YYYYMMDD_HHMMSS.mp3`).
    - `sources_used`: list of URLs used by the agent.

- **Business error (200)**:
  - For cases like "Insufficient verified updates for yesterday." the route returns a JSON error with `status: "error"` and a human-readable `error` field **without raising HTTP 500**.

- **Server error (500)**:
  - Any unexpected failure returns:

```json
{
  "detail": "Internal error message..."
}
```

Orchestrator wraps most known failure paths into a standard error shape before falling back to HTTP 500.

---

### Orchestration Flow (High-Level)

1. **Request received**  
   - `POST /api/v1/generate` with `GenerateRequest`.

2. **Orchestrator initialization**  
   - Compute `yesterday` as `datetime.now() - 1 day` in `YYYY-MM-DD` format.
   - Validate `language` is one of `"en"`, `"hi"`, `"both"`.

3. **Unified agent call**  
   - Build prompt via `build_podcast_prompt(target_date, attribution)`.
   - Call `unified_agent_service.process_podcast_request(...)`.
   - Receive cleaned `eng_pod` and `hin_pod` plus `sources_used`.
   - Persist raw agent output for audit in `storage/raw_data/`.

4. **Script chunking**  
   - Use `split_podcast_scripts` with max length (e.g. 500 chars) and `validate_script_chunks`.

5. **Audio generation**  
   - Depending on `language`:
     - `"en"` — generate English audio only.
     - `"hi"` — generate Hindi audio only.
     - `"both"` — generate both voices.
   - Choose default speakers:
     - English: `"sachit"`
     - Hindi: `"anushka"` (or Hindi-capable voice if selected).

6. **Response assembly**  
   - Prepare `GenerateResponse` payload with scripts, audio URLs, lengths, chunk counts, `sources_used`, and a timestamp.

---

### Error Handling

- **Validation errors** (missing `name`, bad `language` value) are handled by FastAPI / Pydantic:
  - Return HTTP `422` with details.

- **Known business errors** in orchestrator:
  - Invalid `language` enum.
  - Agent did not produce both scripts.
  - Script chunk validation failed.
  - Audio generation failures.
  - Are wrapped using `_error_response(...)` and returned to callers with:

```json
{
  "status": "error",
  "error": "Human-readable message",
  "scripts": {
    "eng_pod": null,
    "hin_pod": null
  },
  "audio": {
    "eng_pod_audio": null,
    "hin_pod_audio": null
  }
}
```

- **Unexpected exceptions** are logged with stack traces and turned into a standardized error JSON, with the route surfacing HTTP `500` where appropriate.

---

### Static Audio Serving

- Audio files are written under `settings.AUDIO_STORAGE_PATH` (default `storage/audio`).
- `app.main` mounts this directory:
  - `app.mount("/audio", StaticFiles(directory=settings.AUDIO_STORAGE_PATH), name="audio")`
- Frontend builds full URLs by combining `REACT_APP_API_URL` (e.g. `http://localhost:8000/api/v1`) and the relative `audio` path, stripping `/api/v1` to point to the bare backend origin.

---

### Notes for Extending the Backend

- Add new endpoints under `app/api/routes_generate.py` and corresponding models under `app/schemas/`.
- Reuse `Settings` from `core/config.py` rather than hard-coding paths or keys.
- When changing the response format of `/generate`, update:
  - `GenerateResponse` schema.
  - This documentation and the main `Finance_AI_Podcast.md` spec.
  - Any frontend code that reads `data.scripts`, `data.audio`, or `data.sources_used`.

