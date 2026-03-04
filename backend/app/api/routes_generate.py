from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.schemas.request_schema import GenerateRequest, PublishPodcastRequest
from app.schemas.response_schema import GenerateResponse
from app.services.orchestrator_service import orchestrator_service
from app.services.unified_agent.agent_init import AGENT_DESCRIPTION
from app.services.unified_agent.prompt_builder import build_podcast_prompt
from app.services.news_service import get_financial_news
from app.services.published_podcasts_store import get_all_podcasts, add_podcast
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


@router.post("/generate")
async def generate_podcast(request: GenerateRequest):
    """
    Generate a finance market brief and podcast.
    Returns 200 with status/error in body so frontend can display the real error message.
    """
    logger.info(f"Received generate request for: {request.name}")
    try:
        result = await orchestrator_service.generate_podcast(
            name=request.name,
            voice_agent=request.voice_agent,
            language=request.language,
            custom_prompt=request.custom_prompt
        )
        return result
    except Exception as e:
        logger.exception("Generate endpoint failed: %s", e)
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "date": "",
                "name": request.name,
                "language": request.language or "both",
                "scripts": {"eng_pod": None, "hin_pod": None},
                "audio": {"eng_pod_audio": None, "hin_pod_audio": None},
                "error": str(e),
                "sources_used": [],
                "timestamp": "",
            },
        )


@router.get("/podcasts")
async def list_podcasts():
    """
    Return all published podcasts (shared across all users).
    Used by the frontend Search tab so everyone sees the same list.
    """
    items = get_all_podcasts()
    return {"items": items, "count": len(items)}


@router.post("/podcasts")
async def publish_podcast(request: PublishPodcastRequest):
    """
    Publish a podcast to the shared list so all users can see and play it.
    Expects a public audio URL (e.g. from Cloudinary or backend /audio/...).
    """
    entry = add_podcast(
        name=request.name,
        description=request.description or "",
        date=request.date,
        lang=request.lang,
        audio_url=request.audioUrl,
    )
    return entry
