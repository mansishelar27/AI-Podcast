import os
import subprocess
from typing import Optional

from app.core.logger import logger

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logger.warning("pydub not installed. Install with: pip install pydub")


def check_ffmpeg() -> Optional[str]:
    """Check if ffmpeg is installed and return its path if found"""
    if not PYDUB_AVAILABLE:
        return None

    ffmpeg_path = None

    # Try to find via `which`
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            ffmpeg_path = result.stdout.strip()
    except Exception:
        pass

    # Common fallback locations
    if not ffmpeg_path:
        for path in ['/usr/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/opt/homebrew/bin/ffmpeg']:
            if os.path.exists(path):
                ffmpeg_path = path
                break

    if ffmpeg_path:
        logger.info(f"✓ ffmpeg found at: {ffmpeg_path}")
        try:
            subprocess.run([ffmpeg_path, '-version'], capture_output=True, check=True)
            logger.info("✓ ffmpeg is fully functional for audio conversion")
            return ffmpeg_path
        except Exception as e:
            logger.warning(f"⚠️ ffmpeg found at {ffmpeg_path} but failed to run: {str(e)}")
            return None
    else:
        logger.warning("⚠️ ffmpeg not found. MP3 conversion will be skipped. Install with: sudo apt-get install ffmpeg")
        return None