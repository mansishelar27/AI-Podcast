import logging
import os
from typing import Optional, Tuple, List

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

try:
    from google.adk.models.lite_llm import LiteLlm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    LiteLlm = None
    logger.warning("LiteLLM not installed. Install with: pip install litellm")


AGENT_DESCRIPTION: str = "Financial market analysis and podcast script generation"

MODELS_WITH_GOOGLE_SEARCH = {
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
}

MODELS_WITHOUT_GOOGLE_SEARCH = {
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
    "gemma-3-27b-it",
    "gemma-3-12b-it",
}


def create_agent(model_name: str, model_type: str = "gemini", api_base: str = None) -> Tuple[Optional["LlmAgent"], Optional[str]]:
    """
    Create an agent with appropriate tool configuration.
    Returns (agent, error_message).
    """
    try:
        if model_type == "gemini":
            model = Gemini(model=model_name)
            tools = [google_search] if google_search and model_name in MODELS_WITH_GOOGLE_SEARCH else []
            
            if model_name in MODELS_WITHOUT_GOOGLE_SEARCH:
                logger.info(f"Model {model_name} doesn't support google_search - using without search tool")
        elif model_type == "huggingface":
            if not LITELLM_AVAILABLE:
                return None, "LiteLLM not available"
            
            hf_token = os.getenv("HF_TOKEN", "")
            model = LiteLlm(
                model=model_name,
                api_base=api_base,
                api_key=hf_token,
            )
            tools = []  # HuggingFace models typically don't support google_search
        else:
            return None, f"Unknown model type: {model_type}"

        agent = LlmAgent(
            name="podcast_generation_agent",
            model=model,
            description=AGENT_DESCRIPTION,
            instruction=(
                "You are a financial research agent. "
                "Research market data and generate professional podcast scripts."
            ),
            tools=tools,
        )
        return agent, None

    except Exception as e:
        return None, str(e)


def initialize_agent() -> Tuple[Optional["LlmAgent"], Optional["InMemorySessionService"], bool]:
    """
    Initialize Google ADK Agent with model fallback chain.
    
    Priority order:
    1. Gemini models WITH google_search (most reliable for web search)
    2. Gemma models WITHOUT google_search (rely on training data)
    3. HuggingFace models (if configured)

    Returns (agent, session_service, success)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False

    if not settings.GEMINI_API_KEY and not os.getenv("HF_TOKEN"):
        logger.error("Neither GEMINI_API_KEY nor HF_TOKEN configured in settings")
        return None, None, False

    model_chain = [
        ("gemini-2.5-flash", "gemini", None, True),
        ("gemini-flash-latest", "gemini", None, True),
        ("gemini-2.0-flash", "gemini", None, True),
        ("gemma-4-31b-it", "gemini", None, False),
        ("gemma-4-26b-a4b-it", "gemini", None, False),
    ]

    hf_model = os.getenv("HF_FALLBACK_MODEL")
    hf_api_base = os.getenv("HF_INFERENCE_API_BASE")
    if hf_model:
        model_chain.append((hf_model, "huggingface", hf_api_base, False))

    for model_name, model_type, api_base, supports_search in model_chain:
        try:
            search_note = "with google_search" if supports_search else "without google_search"
            logger.info(f"Initializing agent with model: {model_name} ({search_note})")

            agent, error = create_agent(model_name, model_type, api_base)
            if agent is None:
                error_lower = error.lower() if error else ""
                if "not supported" in error_lower or "not available" in error_lower:
                    logger.warning(f"Model {model_name} not available: {error}, trying next...")
                    continue
                return None, None, False

            session_service = InMemorySessionService()

            logger.info(f"✓ UnifiedAgentService initialized with model: {model_name}")
            return agent, session_service, True

        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            if any(x in error_lower for x in ["429", "rate limit", "quota", "resource exhausted", "too many requests"]):
                logger.warning(f"Model {model_name} rate limited, trying next fallback...")
                continue

            if "not supported" in error_lower or "google search" in error_lower:
                logger.warning(f"Model {model_name} doesn't support required features: {error_msg}")
                continue

            logger.error(f"Failed to initialize agent with {model_name}: {error_msg}", exc_info=True)
            continue

    logger.error("All models exhausted - all hit rate limits or failed")
    return None, None, False
