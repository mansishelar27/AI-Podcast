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
    # Cloudinary: use CLOUDINARY_URL (recommended) or individual vars
    # Format: cloudinary://api_key:api_secret@cloud_name
    CLOUDINARY_URL: str = os.getenv("CLOUDINARY_URL", "")
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Model Settings
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Storage Paths
    AUDIO_STORAGE_PATH: str = "storage/audio"
    RAW_DATA_STORAGE_PATH: str = "storage/raw_data"
    
    class Config:
        case_sensitive = True

settings = Settings()
