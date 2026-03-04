"""
In-memory + JSON file store for published podcasts so all users see the same list.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List

from app.core.config import settings
from app.core.logger import logger

# Default path for persistence (same directory as raw_data)
PUBLISHED_PODCASTS_FILE = os.path.join(
    os.path.dirname(settings.RAW_DATA_STORAGE_PATH),
    "published_podcasts.json",
)


def _ensure_file_exists() -> None:
    os.makedirs(os.path.dirname(PUBLISHED_PODCASTS_FILE), exist_ok=True)
    if not os.path.isfile(PUBLISHED_PODCASTS_FILE):
        with open(PUBLISHED_PODCASTS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)


def _read_all() -> List[Dict[str, Any]]:
    _ensure_file_exists()
    try:
        with open(PUBLISHED_PODCASTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not read published podcasts: %s", e)
        return []


def _write_all(items: List[Dict[str, Any]]) -> None:
    _ensure_file_exists()
    try:
        with open(PUBLISHED_PODCASTS_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
    except OSError as e:
        logger.error("Could not write published podcasts: %s", e)
        raise


def get_all_podcasts() -> List[Dict[str, Any]]:
    """Return all published podcasts, newest first."""
    items = _read_all()
    # Sort by id descending (newer first)
    items.sort(key=lambda x: x.get("id", 0), reverse=True)
    return items


def add_podcast(
    name: str,
    description: str,
    date: str,
    lang: str,
    audio_url: str,
) -> Dict[str, Any]:
    """Append a published podcast and return the created item with id."""
    items = _read_all()
    new_id = int(datetime.utcnow().timestamp() * 1000)
    created = datetime.utcnow().isoformat() + "Z"
    entry = {
        "id": new_id,
        "name": name,
        "description": description,
        "date": date,
        "lang": lang,
        "audioUrl": audio_url,
        "createdAt": created,
    }
    items.append(entry)
    _write_all(items)
    logger.info("Published podcast added: id=%s name=%s", new_id, name)
    return entry
