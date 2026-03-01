from pydantic import BaseModel, Field
from typing import Optional, Dict, List


class ScriptInfo(BaseModel):
    """Script information"""
    eng_pod: str = Field(..., description="English podcast script")
    hin_pod: str = Field(..., description="Hindi podcast script")


class ScriptLengths(BaseModel):
    """Script length information"""
    eng_pod: int = Field(..., description="English script length in characters")
    hin_pod: int = Field(..., description="Hindi script length in characters")
    total: int = Field(..., description="Total characters (English + Hindi)")


class AudioPaths(BaseModel):
    """Audio file paths"""
    eng_pod_audio: Optional[str] = Field(
        None,
        description="Path to English audio file"
    )
    hin_pod_audio: Optional[str] = Field(
        None,
        description="Path to Hindi audio file"
    )


class ChunkInfo(BaseModel):
    """Chunk information"""
    eng_pod_count: int = Field(..., description="Number of English script chunks")
    hin_pod_count: int = Field(..., description="Number of Hindi script chunks")
    total: int = Field(..., description="Total number of chunks")


class GenerateResponse(BaseModel):
    """
    Response model for successful podcast generation.
    
    Returns:
    - Complete podcast scripts (English + Hindi)
    - Audio file paths based on language selected
    - Script lengths and chunk information
    - Metadata about generation
    """
    status: str = Field(
        ...,
        description="Response status: 'success' or 'error'",
        example="success"
    )
    date: str = Field(
        ...,
        description="Date of podcast generation (YYYY-MM-DD)",
        example="2026-02-26"
    )
    name: str = Field(
        ...,
        description="Podcast name/attribution",
        example="Nippon India Financial"
    )
    attribution: str = Field(
        ...,
        description="Podcast attribution",
        example="Nippon India Financial"
    )
    language: str = Field(
        ...,
        description="Target language: 'en', 'hi', or 'both'",
        example="en"
    )
    scripts: Dict[str, str] = Field(
        ...,
        description="Generated podcast scripts - eng_pod and hin_pod",
        example={
            "eng_pod": "Welcome to the Nippon India Financial Podcast...",
            "hin_pod": "निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है..."
        }
    )
    script_lengths: Dict[str, int] = Field(
        ...,
        description="Length of each script in characters",
        example={
            "eng_pod": 1500,
            "hin_pod": 1600,
            "total": 3100
        }
    )
    audio: Dict[str, Optional[str]] = Field(
        ...,
        description="Paths to generated audio files (based on language parameter)",
        example={
            "eng_pod_audio": "/audio/podcast_en_20260226_120000.mp3",
            "hin_pod_audio": None
        }
    )
    speaker: str = Field(
        ...,
        description="Primary speaker/voice used",
        example="sachit"
    )
    chunks: Dict[str, int] = Field(
        ...,
        description="Information about script chunks",
        example={
            "eng_pod_count": 3,
            "hin_pod_count": 3,
            "total": 6
        }
    )
    error: Optional[str] = Field(
        None,
        description="Error message (None if successful)"
    )
    timestamp: str = Field(
        ...,
        description="Timestamp of generation (ISO format)",
        example="2026-02-26T12:00:00"
    )

    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "date": "2026-02-26",
                "name": "Nippon India Financial",
                "attribution": "Nippon India Financial",
                "language": "en",
                "scripts": {
                    "eng_pod": "Welcome to the Nippon India Financial Podcast. Today's Edition: 2026-02-26. Central banks across the world have been making significant policy decisions...",
                    "hin_pod": "निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: 2026-02-26। विश्व भर के केंद्रीय बैंक ऐसे नीतिगत निर्णय ले रहे हैं..."
                },
                "script_lengths": {
                    "eng_pod": 1500,
                    "hin_pod": 1600,
                    "total": 3100
                },
                "audio": {
                    "eng_pod_audio": "/audio/podcast_en_20260226_120000.mp3",
                    "hin_pod_audio": None
                },
                "speaker": "sachit",
                "chunks": {
                    "eng_pod_count": 3,
                    "hin_pod_count": 3,
                    "total": 6
                },
                "error": None,
                "timestamp": "2026-02-26T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = Field(
        "error",
        description="Response status: 'error'",
        example="error"
    )
    date: str = Field(
        ...,
        description="Date when error occurred",
        example="2026-02-26"
    )
    name: str = Field(
        ...,
        description="Podcast name provided in request",
        example="Nippon India Financial"
    )
    language: str = Field(
        ...,
        description="Language parameter from request",
        example="en"
    )
    scripts: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Scripts (None on error)"
    )
    audio: Optional[Dict[str, Optional[str]]] = Field(
        None,
        description="Audio paths (None on error)"
    )
    error: str = Field(
        ...,
        description="Error message",
        example="Invalid language: xyz. Use 'en', 'hi', or 'both'"
    )
    timestamp: str = Field(
        ...,
        description="Timestamp of error (ISO format)",
        example="2026-02-26T12:00:00"
    )

    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "date": "2026-02-26",
                "name": "Nippon India Financial",
                "language": "en",
                "scripts": None,
                "audio": None,
                "error": "Invalid language: xyz. Use 'en', 'hi', or 'both'",
                "timestamp": "2026-02-26T12:00:00"
            }
        }


class LanguageOption(BaseModel):
    """Information about a language option"""
    name: str = Field(..., description="Language name")
    default_speaker: Optional[str] = Field(None, description="Default speaker")
    available_speakers: List[str] = Field(..., description="List of available speakers")


class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages endpoint"""
    status: str = Field("success", example="success")
    supported_languages: Dict[str, dict] = Field(
        ...,
        description="Dictionary of supported languages and their speakers",
        example={
            "en": {
                "name": "English",
                "default_speaker": "sachit",
                "available_speakers": ["sachit", "anushka"]
            },
            "hi": {
                "name": "Hindi",
                "default_speaker": "anushka",
                "available_speakers": ["anushka", "karan"]
            },
            "both": {
                "name": "Bilingual (English + Hindi)",
                "default_speakers": {"en": "sachit", "hi": "anushka"},
                "description": "Generates both English and Hindi audio"
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field("healthy", example="healthy")
    service: str = Field("podcast-generation", example="podcast-generation")
    message: str = Field(
        "Podcast generation service is running",
        example="Podcast generation service is running"
    )