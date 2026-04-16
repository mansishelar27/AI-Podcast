import logging
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


def initialize_agent() -> Tuple[Optional["LlmAgent"], Optional["InMemorySessionService"], bool]:
    """
    Initialize Google ADK Agent with Gemini models and Google Search.

    Returns (agent, session_service, success)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False

    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured in settings")
        return None, None, False

    if not google_search:
        logger.error("google_search tool not available")
        return None, None, False

    model_chain = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
    ]

    for model_name in model_chain:
        try:
            logger.info(f"Initializing agent with model: {model_name}")

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

            logger.info(f"✓ UnifiedAgentService initialized with model: {model_name}")
            return agent, session_service, True

        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            if any(x in error_lower for x in ["429", "503", "rate limit", "quota", "unavailable", "resource exhausted", "too many requests"]):
                logger.warning(f"Model {model_name} rate limited, trying next...")
                continue

            logger.error(f"Failed to initialize agent with {model_name}: {error_msg}", exc_info=True)
            continue

    logger.error("All models exhausted")
    return None, None, False
