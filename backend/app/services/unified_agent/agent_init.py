import logging
import os
from typing import Optional, Tuple, Dict, Any

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

MODEL_CONFIGS = {
    "gemma-4-26b-a4b-it": {
        "type": "gemini",
        "description": "Gemma 4 26B MoE (efficient)",
    },
    "gemma-4-31b-it": {
        "type": "gemini",
        "description": "Gemma 4 31B (larger, better quality)",
    },
    "gemini-2.5-flash": {
        "type": "gemini",
        "description": "Gemini Flash 2.5 (fast, reliable)",
    },
    "gemini-flash-latest": {
        "type": "gemini",
        "description": "Gemini Flash latest (auto-updates)",
    },
}


def create_gemini_agent(model_name: str) -> "LlmAgent":
    """Create an agent using Gemini model (native Gemma or Gemini)."""
    return LlmAgent(
        name="podcast_generation_agent",
        model=Gemini(model=model_name),
        description=AGENT_DESCRIPTION,
        instruction=(
            "You are a financial research agent. "
            "Research market data and generate professional podcast scripts."
        ),
        tools=[google_search] if google_search else [],
    )


def create_huggingface_agent(model_name: str, api_base: str = None) -> Optional["LlmAgent"]:
    """Create an agent using HuggingFace Inference Endpoint via LiteLLM."""
    if not LITELLM_AVAILABLE:
        logger.warning("LiteLLM not available. Cannot create HuggingFace agent.")
        return None

    hf_token = os.getenv("HF_TOKEN", "")

    try:
        agent = LlmAgent(
            model=LiteLlm(
                model=model_name,
                api_base=api_base,
                api_key=hf_token,
            ),
            name="podcast_generation_agent",
            description=AGENT_DESCRIPTION,
            instruction=(
                "You are a financial research agent. "
                "Research market data and generate professional podcast scripts."
            ),
            tools=[google_search] if google_search else [],
        )
        return agent
    except Exception as e:
        logger.error(f"Failed to create HuggingFace agent: {e}")
        return None


def initialize_agent() -> Tuple[Optional["LlmAgent"], Optional["InMemorySessionService"], bool]:
    """
    Initialize Google ADK Agent with model fallback chain.
    Priority: Gemma 4 26B → Gemma 4 31B → Gemini Flash 2.5 → HuggingFace

    Returns (agent, session_service, success)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False

    if not settings.GEMINI_API_KEY and not os.getenv("HF_TOKEN"):
        logger.error("Neither GEMINI_API_KEY nor HF_TOKEN configured in settings")
        return None, None, False

    model_chain = [
        ("gemma-4-26b-a4b-it", "gemini", None),
        ("gemma-4-31b-it", "gemini", None),
        ("gemini-2.5-flash", "gemini", None),
        ("gemini-flash-latest", "gemini", None),
    ]

    hf_model = os.getenv("HF_FALLBACK_MODEL")
    hf_api_base = os.getenv("HF_INFERENCE_API_BASE")
    if hf_model:
        model_chain.append((hf_model, "huggingface", hf_api_base))

    for model_name, model_type, api_base in model_chain:
        try:
            logger.info(f"Initializing agent with model: {model_name} (type: {model_type})")

            if model_type == "gemini":
                agent = create_gemini_agent(model_name)
            elif model_type == "huggingface":
                agent = create_huggingface_agent(model_name, api_base)
                if agent is None:
                    continue
            else:
                logger.warning(f"Unknown model type: {model_type}")
                continue

            session_service = InMemorySessionService()

            logger.info(f"✓ UnifiedAgentService initialized with model: {model_name}")
            return agent, session_service, True

        except Exception as e:
            error_lower = str(e).lower()
            if any(x in error_lower for x in ["429", "rate limit", "quota", "resource exhausted", "too many requests"]):
                logger.warning(f"Model {model_name} rate limited, trying next fallback...")
                continue

            logger.error(f"Failed to initialize agent with {model_name}: {str(e)}", exc_info=True)
            continue

    logger.error("All models exhausted - all hit rate limits or failed")
    return None, None, False
