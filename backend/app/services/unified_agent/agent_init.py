from typing import Optional, Tuple

from app.core.config import settings
from app.core.logger import logger

try:
    from google.adk.agents import LlmAgent
    from google.adk.models import Gemini
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    LlmAgent = None
    Gemini = None
    Runner = None
    InMemorySessionService = None
    google_search = None
    logger.warning("Google ADK not installed. Install with: pip install google-adk")


AGENT_DESCRIPTION: str = "Financial market analysis and podcast script generation"


def initialize_agent(
    force_provider: Optional[str] = None,
) -> Tuple[Optional["LlmAgent"], Optional["InMemorySessionService"], bool, Optional[str], Optional[str]]:
    """
    Initialize Google ADK Agent with Google Search.

    Returns (agent, session_service, success, provider, model_name)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False, None, None

    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured in settings")
        return None, None, False, None, None

    if not google_search:
        logger.error("google_search tool not available")
        return None, None, False, None, None

    # Planned Claude-primary chain (kept commented until Vertex/ADK Claude runtime is enabled):
    # from google.adk.models.anthropic_llm import Claude
    # from google.adk.models.registry import LLMRegistry
    # if settings.CLAUDE_VERTEX_ENABLED:
    #     LLMRegistry.register(Claude)
    #     model_chain = [
    #         ("claude_vertex", settings.CLAUDE_VERTEX_MODEL),
    #         ("gemini", settings.GEMINI_MODEL),
    #         ("gemini", "gemini-flash-latest"),
    #     ]
    # else:
    #     model_chain = [
    #         ("gemini", settings.GEMINI_MODEL),
    #         ("gemini", "gemini-flash-latest"),
    #     ]

    # Active chain for current phase: Gemini only.
    model_chain = [
        ("gemini", settings.GEMINI_MODEL),
        ("gemini", "gemini-flash-latest"),
    ]
    if force_provider == "gemini":
        logger.info("Forced provider requested: gemini")

    for provider, model_name in model_chain:
        try:
            logger.info(
                "Initializing agent with provider=%s model=%s",
                provider,
                model_name,
            )

            agent = LlmAgent(
                name="podcast_generation_agent",
                model=Gemini(model=model_name),
                description=AGENT_DESCRIPTION,
                instruction=(
                    "You are a financial research agent. "
                    "Research market data and generate professional podcast scripts. "
                    "Use the google_search tool to get current financial news, stock prices, "
                    "market trends, and economic data from the internet."
                ),
                tools=[google_search],
            )

            session_service = InMemorySessionService()

            logger.info(
                "✓ UnifiedAgentService initialized with provider=%s model=%s",
                provider,
                model_name,
            )
            return agent, session_service, True, provider, model_name

        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            if any(x in error_lower for x in ["429", "503", "rate limit", "quota", "unavailable", "resource exhausted", "too many requests"]):
                logger.warning(f"Model {model_name} rate limited, trying next...")
                continue

            logger.error(f"Failed to initialize agent with {model_name}: {error_msg}", exc_info=True)
            continue

    logger.error("All models exhausted")
    return None, None, False, None, None
