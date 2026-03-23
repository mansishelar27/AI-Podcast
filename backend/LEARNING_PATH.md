# FastAPI Project — Learning Path (Start Here!)

**For beginners:** Follow this order to understand how the backend works and how files connect.

---

## 📍 Step 1: Entry Point — `app/main.py`

**Start here.** This is where the FastAPI app is created and configured.

| What to notice |
|----------------|
| `app = FastAPI(...)` — the main application object |
| `app.add_middleware(CORSMiddleware, ...)` — allows frontend (port 3000) to call backend (port 8000) |
| `app.mount("/audio", StaticFiles(...))` — serves MP3 files from `storage/audio/` at `/audio/...` |
| `app.include_router(routes_generate.router, prefix="/api/v1")` — all API routes live under `/api/v1` |

**Flow:** `main.py` imports `routes_generate` and mounts it at `/api/v1`. So `/api/v1/generate`, `/api/v1/podcasts`, etc. are defined elsewhere.

---

## 📍 Step 2: Config — `app/core/config.py`

**Read this next.** It loads settings from `.env` and environment variables.

| Key settings |
|--------------|
| `GEMINI_API_KEY`, `SARVAM_API_KEY` — for AI and TTS |
| `CLOUDINARY_*` — for cloud upload |
| `AUDIO_STORAGE_PATH`, `RAW_DATA_STORAGE_PATH` — where files are saved |
| `API_V1_STR` — prefix for routes (`/api/v1`) |

**Flow:** All services import `from app.core.config import settings` to get these values.

---

## 📍 Step 3: API Routes — `app/api/routes_generate.py`

**This is the HTTP layer.** Each `@router.get(...)` or `@router.post(...)` is an endpoint.

| Endpoint | What it does | Calls |
|----------|--------------|-------|
| `GET /agent-info` | Returns agent description | `AGENT_DESCRIPTION` from agent_init |
| `GET /agent-instruction` | Returns default prompt | `build_podcast_prompt()` |
| `GET /financial-news` | Returns RSS news items | `get_financial_news()` |
| `POST /generate` | **Main flow** — generates podcast | `orchestrator_service.generate_podcast()` |
| `GET /podcasts` | List all published podcasts | `get_all_podcasts()` |
| `POST /podcasts` | Publish a podcast | `add_podcast()` |

**Flow:** Routes receive HTTP requests, validate with Pydantic schemas (`GenerateRequest`, etc.), call services, and return JSON.

---

## 📍 Step 4: Schemas — `app/schemas/`

**Request/Response shapes:**

- `request_schema.py` — `GenerateRequest` (name, voice_agent, language, custom_prompt), `PublishPodcastRequest`
- `response_schema.py` — `GenerateResponse` (status, scripts, audio, etc.)

FastAPI uses these for automatic validation and OpenAPI docs.

---

## 📍 Step 5: Orchestrator — `app/services/orchestrator_service.py`

**Central coordinator.** When you call `POST /generate`, the orchestrator runs the full pipeline:

```
1. unified_agent_service.process_podcast_request()  →  English + Hindi scripts
2. split_podcast_scripts()                           →  Chunk scripts for TTS
3. podcast_service.generate_audio_*()               →  MP3 files (Sarvam TTS)
4. upload_mp3() [Cloudinary]                        →  Public URLs
5. Return JSON with scripts + audio URLs
```

**Flow:** `routes_generate.py` → `orchestrator_service.generate_podcast()` → calls other services in sequence.

---

## 📍 Step 6: Unified Agent (Script Generation) — `app/services/unified_agent/`

**This is where the AI magic happens.**

| File | Role |
|------|------|
| `agent_init.py` | Creates Google ADK Agent + InMemorySessionService, configures Gemini model |
| `prompt_builder.py` | Builds the long prompt sent to the agent (what to research, format, etc.) |
| `service.py` | `UnifiedAgentService` — calls `run_agent_and_get_script()`, cleans output |
| `runner_execution.py` | Runs the agent with Runner, streams response, splits into eng_pod/hin_pod |
| `script_cleaner.py` | Cleans raw LLM output (markers, extra text) |
| `error_handling.py` | `error_response()` helper |

**Flow:** `orchestrator` → `unified_agent_service.process_podcast_request()` → `runner_execution.run_agent_and_get_script()` → Agent uses `google_search` tool + Gemini to generate scripts.

---

## 📍 Step 7: Podcast / Audio — `app/services/podcast/`

**Turns text into MP3.**

| File | Role |
|------|------|
| `audio.py` | `generate_audio_from_script()`, `generate_podcast_audio()` — calls Sarvam TTS API, combines chunks, saves MP3 |
| `script_splitting.py` | Splits long scripts into chunks (max ~500 chars) for Sarvam |
| `service.py` | `PodcastService` — high-level wrapper |
| `ffmpeg_check.py` | Checks pydub/ffmpeg for audio conversion |

**Flow:** `orchestrator` → `podcast_service.generate_audio_from_script()` or `generate_podcast_audio()` → Sarvam API → MP3 saved to `storage/audio/`.

---

## 📍 Step 8: Cloudinary — `app/services/cloudinary_service.py`

**Uploads MP3 to cloud.**

- `upload_mp3(file_path, public_id)` — uploads file, returns `secure_url`
- Orchestrator calls this after audio is generated, replaces local path with Cloudinary URL in response

---

## 📍 Step 9: Supporting Services

| File | Role |
|------|------|
| `news_service.py` | Fetches RSS feeds (Economic Times, MoneyControl, etc.), returns unified list |
| `published_podcasts_store.py` | Reads/writes `storage/published_podcasts.json` — shared list of published podcasts |

---

## 🔄 Request Flow Diagram (POST /generate)

```
Frontend                    Backend
   |                           |
   |  POST /api/v1/generate    |
   |  { name, language, ... }   |
   |-------------------------->| routes_generate.py
   |                           |     |
   |                           |     v
   |                           | orchestrator_service.generate_podcast()
   |                           |     |
   |                           |     +---> unified_agent (Gemini + google_search)
   |                           |     |         --> eng_pod, hin_pod scripts
   |                           |     |
   |                           |     +---> podcast/audio (Sarvam TTS)
   |                           |     |         --> MP3 files in storage/audio/
   |                           |     |
   |                           |     +---> cloudinary_service.upload_mp3()
   |                           |               --> Cloudinary URL
   |                           |     |
   |                           |     +---> return { scripts, audio: { eng_pod_audio, hin_pod_audio } }
   |                           |
   |<--------------------------| 200 OK + JSON
   |
```

---

## ✅ Recommended Reading Order

1. `app/main.py`
2. `app/core/config.py`
3. `app/api/routes_generate.py`
4. `app/schemas/request_schema.py`
5. `app/services/orchestrator_service.py` (main logic)
6. `app/services/unified_agent/agent_init.py` → `service.py` → `runner_execution.py`
7. `app/services/podcast/audio.py` (focus on `generate_audio_from_script`)
8. `app/services/cloudinary_service.py`
9. `app/services/news_service.py`, `published_podcasts_store.py`

---

## 🎯 FastAPI Concepts You'll See

| Concept | Where |
|---------|-------|
| **APIRouter** | `routes_generate.py` — groups related endpoints |
| **Request body validation** | `GenerateRequest`, `PublishPodcastRequest` — Pydantic models |
| **Path / query params** | `get_agent_instruction(date=..., attribution=...)` |
| **Async endpoints** | `async def generate_podcast(...)` — allows non-blocking I/O |
| **Middleware** | CORS in `main.py` |

---

*Happy learning!*
