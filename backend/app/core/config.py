import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Always load .env from backend folder (fixes localhost: loading when started from project root)
_backend_dir = Path(__file__).resolve().parent.parent.parent
_env_path = _backend_dir / ".env"
load_dotenv(_env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Finance AI Podcast Generator"
    API_V1_STR: str = "/api/v1"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    # Cloudinary: use CLOUDINARY_URL (recommended) or individual vars
    # Format: cloudinary://api_key:api_secret@cloud_name
    CLOUDINARY_URL: str = os.getenv("CLOUDINARY_URL", "")
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Model Settings - ADK uses models in v1beta API
    # Valid models: gemini-1.5-flash, gemini-2.0-flash, gemini-2.0-flash-lite, gemini-2.5-flash
    GEMINI_MODEL: str = "gemini-2.5-flash"
    # Fallback models
    GEMINI_MODEL_FALLBACK: str = "gemini-2.0-flash-lite"
    
    # Storage Paths - use absolute paths for proper static file serving
    AUDIO_STORAGE_PATH: str = os.path.join(str(_backend_dir), "storage/audio")
    RAW_DATA_STORAGE_PATH: str = os.path.join(str(_backend_dir), "storage/raw_data")
    # Intro music file path - set INTRO_MUSIC_PATH env var to point to your intro music file
    # Default looks for intro music in storage/audio folder
    INTRO_MUSIC_PATH: str = os.getenv("INTRO_MUSIC_PATH", os.path.join(str(_backend_dir), "storage/audio/Nippon India Mutual Fund MOGOSCAPE®(2).mp3"))
    
    def _resolve_intro_music_path(self) -> str:
        """Return the intro music file path if it exists."""
        path = self.INTRO_MUSIC_PATH
        if path and os.path.exists(path):
            return path
        return ""

    class Config:
        case_sensitive = True

settings = Settings()
