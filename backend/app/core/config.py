import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Finance AI Podcast Generator"
    API_V1_STR: str = "/api/v1"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    
    # Model Settings
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Storage Paths
    AUDIO_STORAGE_PATH: str = "storage/audio"
    RAW_DATA_STORAGE_PATH: str = "storage/raw_data"
    
    class Config:
        case_sensitive = True

settings = Settings()
