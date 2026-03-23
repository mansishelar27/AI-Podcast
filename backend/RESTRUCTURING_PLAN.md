# Backend Restructuring Plan

A small, optional restructuring to improve maintainability **without changing behavior**.

---

## Current Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes_generate.py      # All routes in one file
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   ├── schemas/
│   │   ├── request_schema.py
│   │   └── response_schema.py
│   ├── services/
│   │   ├── podcast/                # audio, file_utils, ffmpeg_check, script_splitting, service
│   │   ├── unified_agent/          # agent_init, error_handling, prompt_builder, runner_execution, script_cleaner, service
│   │   ├── cloudinary_service.py
│   │   ├── news_service.py
│   │   ├── orchestrator_service.py
│   │   └── published_podcasts_store.py
│   └── main.py
├── storage/
├── .env
├── .env.example
└── requirements.txt
```

---

## Proposed Changes (Low Risk)

### 1. Add Package `__init__.py` Files (Optional but Recommended)

Ensures clean package imports and avoids edge cases with Python path resolution.

| Add file | Purpose |
|----------|---------|
| `app/__init__.py` | Empty or `""` |
| `app/api/__init__.py` | Empty |
| `app/core/__init__.py` | Empty |
| `app/schemas/__init__.py` | Empty |
| `app/services/__init__.py` | Empty |
| `app/services/podcast/__init__.py` | Empty |
| `app/services/unified_agent/__init__.py` | Empty |

**Effort:** 1 min · **Risk:** None

---

### 2. Move `main.py` to Backend Root (Optional)

**Before:** `backend/app/main.py` → run with `uvicorn app.main:app`  
**After:** `backend/main.py` → run with `uvicorn main:app`

**Benefits:**
- Clear separation: `app/` = application code, `main.py` = entry point
- Simpler run command for newcomers

**Required changes:**
1. Create `backend/main.py` that imports and re-exports:
   ```python
   from app.main import app
   __all__ = ["app"]
   ```
2. Keep `app/main.py` for now (or move its contents to `backend/main.py` and update imports)
3. Update `requirements.txt` / docs / Render config: `uvicorn main:app`

**Effort:** ~5 min · **Risk:** Low (only entry point changes)

---

### 3. Split Routes by Domain (When Scale Justifies It)

Currently all routes live in `routes_generate.py`. When the file grows (e.g. 10+ endpoints), consider:

| New file | Endpoints |
|----------|-----------|
| `api/routes_generate.py` | `/generate` |
| `api/routes_podcasts.py` | `/podcasts` (GET, POST) |
| `api/routes_news.py` | `/financial-news`, `/agent-info`, `/agent-instruction` |

In `main.py`:
```python
app.include_router(routes_generate.router, prefix="/api/v1", tags=["Generate"])
app.include_router(routes_podcasts.router, prefix="/api/v1", tags=["Podcasts"])
app.include_router(routes_news.router, prefix="/api/v1", tags=["News"])
```

**Effort:** ~15 min · **Risk:** Low · **When:** Only when routes become hard to navigate

---

### 4. Add `models/` Directory (When DB Is Introduced)

If you add a database (SQLAlchemy, etc.), create:

```
app/
├── models/
│   ├── __init__.py
│   └── podcast.py    # DB models
```

Keep schemas (request/response) in `schemas/`; use `models/` for ORM/DB entities.

**When:** When you introduce a database.

---

## What Not to Change

- **Services layout** — `podcast/`, `unified_agent/`, and top-level services are already well organized
- **Config and logger** — `core/` is appropriate
- **Schemas** — Single files per concern is fine for current size

---

## Summary

| Change | Priority | Effort | Do Now? |
|--------|----------|--------|---------|
| Add `__init__.py` | High | 1 min | Yes |
| Move main.py to root | Medium | 5 min | Optional |
| Split routes | Low | 15 min | When file grows |
| Add `models/` | N/A | — | When adding DB |

Implement steps 1–2 when convenient; the rest can wait until the codebase grows.
