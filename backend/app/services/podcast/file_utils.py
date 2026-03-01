import os
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.logger import logger


async def save_script(script: str, topic: str = "podcast") -> Optional[str]:
    """Saves the generated script to a .txt file."""
    try:
        clean_topic = "".join([c if c.isalnum() else "_" for c in topic]).strip("_")
        if not clean_topic:
            clean_topic = "podcast"

        filename = f"{clean_topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(settings.RAW_DATA_STORAGE_PATH, filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(script)

        logger.info(f"✓ Podcast script saved: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Failed to save podcast script: {str(e)}")
        return None