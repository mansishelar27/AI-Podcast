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


# Single source of truth for agent description so backend + frontend can display it
AGENT_DESCRIPTION: str = "Financial market analysis and podcast script generation"


def initialize_agent() -> Tuple[Optional["Agent"], Optional["InMemorySessionService"], bool]:
    """
    Initialize Google ADK Agent and SessionService.
    Tries primary model first, falls back to secondary if rate limited.
    Returns (agent, session_service, success)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False

    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured in settings")
        return None, None, False

    models_to_try = [
        settings.GEMINI_MODEL,
        settings.GEMINI_MODEL_FALLBACK,
    ]
    
    for model_name in models_to_try:
        try:
            logger.info(f"Initializing agent with model: {model_name}")
            
            generate_config = None
            if genai_types is not None:
                generate_config = genai_types.GenerateContentConfig(
                    max_output_tokens=8192,
                    temperature=0.7,
                )

            agent = Agent(
                name="podcast_generation_agent",
                model=model_name,
                description=AGENT_DESCRIPTION,
                instruction=(
                    "You are a financial research agent. "
                    "Research market data and generate professional podcast scripts."
                ),
                tools=[google_search],
                generate_content_config=generate_config,
            )

            session_service = InMemorySessionService()

            logger.info(f"✓ UnifiedAgentService initialized with model: {model_name}")
            return agent, session_service, True

        except Exception as e:
            error_lower = str(e).lower()
            # Check if it's a rate limit error - try next model
            if "429" in error_lower or "rate limit" in error_lower or "quota" in error_lower:
                logger.warning(f"Model {model_name} rate limited, trying fallback...")
                continue
            
            logger.error(f"Failed to initialize ADK agent: {str(e)}", exc_info=True)
            return None, None, False
    
    logger.error("All models exhausted - all hit rate limits")
    return None, None, False