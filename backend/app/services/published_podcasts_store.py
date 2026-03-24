"""
Persistent podcast store backed by Supabase (free PostgreSQL cloud database).

Why Supabase instead of a local file:
  Render uses an ephemeral filesystem — any file written at runtime is wiped
  when the container restarts or goes to sleep. Supabase stores the podcast
  list permanently in the cloud so all users always see the same list.

Setup (one-time):
  1. Sign up free at https://supabase.com
  2. Create a project, then run this SQL in the SQL Editor:

       CREATE TABLE podcasts (
         id          BIGINT PRIMARY KEY,
         name        TEXT,
         description TEXT,
         date        TEXT,
         lang        TEXT,
         audio_url   TEXT,
         created_at  TEXT
       );

  3. Go to Project Settings → API and copy:
       - Project URL  →  SUPABASE_URL
       - anon/public key  →  SUPABASE_KEY
  4. Add both to your .env (local) and Render environment variables.

Fallback:
  If SUPABASE_URL or SUPABASE_KEY are not set, the store silently falls back
  to the original local JSON file (useful for local development without Supabase).
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List

import requests

from app.core.config import settings
from app.core.logger import logger

# ── Supabase config ───────────────────────────────────────────────────────────
_SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
_TABLE        = "podcasts"
_REST_URL     = f"{_SUPABASE_URL}/rest/v1/{_TABLE}"

_SUPABASE_HEADERS = {
    "apikey":        _SUPABASE_KEY,
    "Authorization": f"Bearer {_SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=representation",   # return the inserted row
}

_USE_SUPABASE = bool(_SUPABASE_URL and _SUPABASE_KEY)

# Log at startup so you can verify in Render logs which mode is active
import logging as _logging
_startup_logger = _logging.getLogger(__name__)
if _USE_SUPABASE:
    _startup_logger.info("PodcastStore: using Supabase at %s", _SUPABASE_URL)
else:
    _startup_logger.warning(
        "PodcastStore: SUPABASE_URL/SUPABASE_KEY not set — "
        "falling back to local file (data will be lost on Render restart!)"
    )

# ── Local file fallback (localhost dev without Supabase) ──────────────────────
_LOCAL_FILE = os.path.join(
    os.path.dirname(settings.RAW_DATA_STORAGE_PATH),
    "published_podcasts.json",
)


# ── Supabase helpers ──────────────────────────────────────────────────────────

def _supabase_read() -> List[Dict[str, Any]]:
    """Fetch all rows from Supabase, ordered newest first."""
    try:
        resp = requests.get(
            _REST_URL,
            headers={**_SUPABASE_HEADERS, "Prefer": ""},
            params={"order": "id.desc"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json() if isinstance(resp.json(), list) else []
    except Exception as e:
        logger.warning("Supabase read failed: %s", e)
        return []


def _supabase_insert(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Insert one row into Supabase and return the created row."""
    # Map Python dict keys → Supabase column names
    row = {
        "id":          entry["id"],
        "name":        entry["name"],
        "description": entry.get("description", ""),
        "date":        entry.get("date", ""),
        "lang":        entry.get("lang", ""),
        "audio_url":   entry.get("audioUrl", ""),
        "created_at":  entry.get("createdAt", ""),
    }
    try:
        resp = requests.post(
            _REST_URL,
            headers=_SUPABASE_HEADERS,
            data=json.dumps(row),
            timeout=10,
        )
        resp.raise_for_status()
        created = resp.json()
        # Supabase returns a list when Prefer: return=representation
        if isinstance(created, list) and created:
            created = created[0]
        # Re-map audio_url → audioUrl for frontend consistency
        if isinstance(created, dict) and "audio_url" in created:
            created["audioUrl"] = created.pop("audio_url")
        return created if isinstance(created, dict) else row
    except Exception as e:
        logger.error("Supabase insert failed: %s", e)
        raise


# ── Local file helpers (fallback) ─────────────────────────────────────────────

def _local_ensure() -> None:
    os.makedirs(os.path.dirname(_LOCAL_FILE), exist_ok=True)
    if not os.path.isfile(_LOCAL_FILE):
        with open(_LOCAL_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)


def _local_read() -> List[Dict[str, Any]]:
    _local_ensure()
    try:
        with open(_LOCAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Local podcast file read failed: %s", e)
        return []


def _local_write(items: List[Dict[str, Any]]) -> None:
    _local_ensure()
    try:
        with open(_LOCAL_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.error("Local podcast file write failed: %s", e)
        raise


# ── Public API ────────────────────────────────────────────────────────────────

def get_all_podcasts() -> List[Dict[str, Any]]:
    """Return all published podcasts, newest first."""
    if _USE_SUPABASE:
        rows = _supabase_read()
        # Normalise column name for frontend
        for r in rows:
            if "audio_url" in r and "audioUrl" not in r:
                r["audioUrl"] = r.pop("audio_url")
        return rows
    # Local fallback
    items = _local_read()
    items.sort(key=lambda x: x.get("id", 0), reverse=True)
    return items


def add_podcast(
    name: str,
    description: str,
    date: str,
    lang: str,
    audio_url: str,
) -> Dict[str, Any]:
    """Append a published podcast and return the created entry."""
    new_id  = int(datetime.utcnow().timestamp() * 1000)
    created = datetime.utcnow().isoformat() + "Z"
    entry = {
        "id":          new_id,
        "name":        name,
        "description": description,
        "date":        date,
        "lang":        lang,
        "audioUrl":    audio_url,
        "createdAt":   created,
    }

    if _USE_SUPABASE:
        result = _supabase_insert(entry)
        logger.info("Podcast published to Supabase: id=%s name=%s", new_id, name)
        return result

    # Local fallback
    items = _local_read()
    items.append(entry)
    _local_write(items)
    logger.info("Podcast published to local file: id=%s name=%s", new_id, name)
    return entry
