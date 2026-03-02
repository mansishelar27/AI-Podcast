from fastapi import APIRouter, HTTPException
from app.schemas.request_schema import GenerateRequest
from app.schemas.response_schema import GenerateResponse
from app.services.orchestrator_service import orchestrator_service
from app.services.unified_agent.agent_init import AGENT_DESCRIPTION
from app.services.unified_agent.prompt_builder import build_podcast_prompt
from app.services.news_service import get_financial_news
from app.core.logger import logger

router = APIRouter()


@router.get("/agent-info")
async def get_agent_info():
    """
    Return basic metadata about the unified agent so the frontend can
    display an \"Agent description\" without duplicating strings.
    """
    return {"description": AGENT_DESCRIPTION}


@router.get("/agent-instruction")
async def get_agent_instruction(
    date: str = "yesterday",
    attribution: str = "Smart Finance Agent"
):
    """
    Return the default agent instruction (prompt) from prompt_builder.
    Frontend can display this and optionally send a modified version
    as custom_prompt when generating (session-only).
    """
    instruction = build_podcast_prompt(target_date=date, attribution=attribution)
    return {"instruction": instruction}


@router.get("/financial-news")
async def financial_news(limit: int = 25):
    """
    Return latest stock market and major financial news (automated from RSS feeds).
    Used by the homepage news column.
    """
    items = await get_financial_news(limit=min(limit, 50))
    return {"items": items, "count": len(items)}


@router.post("/generate", response_model=GenerateResponse)
async def generate_podcast(request: GenerateRequest):
    """
    Generate a finance market brief and podcast.
    """
    logger.info(f"Received generate request for: {request.name}")
    result = await orchestrator_service.generate_podcast(
        name=request.name,
        voice_agent=request.voice_agent,
        language=request.language,
        custom_prompt=request.custom_prompt
    )
    
    if result["status"] == "error":
        if result["error"] == "Insufficient verified updates for yesterday.":
            # This is a business error, not a server error
            return result
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result
