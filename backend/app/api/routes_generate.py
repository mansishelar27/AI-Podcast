from fastapi import APIRouter, HTTPException
from app.schemas.request_schema import GenerateRequest
from app.schemas.response_schema import GenerateResponse
from app.services.orchestrator_service import orchestrator_service
from app.core.logger import logger

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate_podcast(request: GenerateRequest):
    """
    Generate a finance market brief and podcast.
    """
    logger.info(f"Received generate request for: {request.name}")
    result = await orchestrator_service.generate_podcast(
        name=request.name,
        voice_agent=request.voice_agent,
        language=request.language
    )
    
    if result["status"] == "error":
        if result["error"] == "Insufficient verified updates for yesterday.":
            # This is a business error, not a server error
            return result
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result
