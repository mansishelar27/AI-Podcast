from pydantic import BaseModel, Field
from typing import Optional

class GenerateRequest(BaseModel):
    """Request model for podcast generation with language support"""
    name: str = Field(
        ...,
        description="Podcast name/attribution (e.g., 'Nippon India Financial')",
        min_length=1,
        example="Nippon India Financial"
    )
    voice_agent: Optional[str] = Field(
        None,
        description="Speaker/voice name (e.g., 'sachit' for English, 'anushka' for Hindi)",
        example="sachit"
    )
    language: str = Field(
        "both",
        description="Target language: 'en' (English only), 'hi' (Hindi only), or 'both' (default)",
        pattern="^(en|hi|both)$",
        example="en"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Nippon India Financial",
                "voice_agent": "sachit",
                "language": "en"
            }
        }