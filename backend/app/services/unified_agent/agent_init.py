import logging
from typing import Optional, Tuple

from app.core.config import settings
from app.core.logger import logger

try:
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.adk.tools import google_search
    from google.genai import types as genai_types
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    genai_types = None
    logger.warning("Google ADK not installed. Install with: pip install google-adk")


def initialize_agent() -> Tuple[Optional["Agent"], Optional["InMemorySessionService"], bool]:
    """
    Initialize Google ADK Agent and SessionService.
    Returns (agent, session_service, success)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False

    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured in settings")
        return None, None, False

    try:
        # Allow long output so full English + Hindi scripts are not truncated (~8000 tokens for 1000+ words each)
        generate_config = None
        if genai_types is not None:
            generate_config = genai_types.GenerateContentConfig(max_output_tokens=8192)

        agent = Agent(
            name="podcast_generation_agent",
            model=settings.GEMINI_MODEL,
            description="Financial market analysis and podcast script generation",
            instruction=(
                "You are a financial research agent. "
                "Research market data and generate professional podcast scripts."
            ),
            tools=[google_search],
            generate_content_config=generate_config,
        )

        session_service = InMemorySessionService()

        logger.info("✓ UnifiedAgentService components initialized successfully")
        return agent, session_service, True

    except Exception as e:
        logger.error(f"Failed to initialize ADK agent: {str(e)}", exc_info=True)
        return None, None, False