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
    from google.adk.tools import FunctionTool
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    LlmAgent = None
    Gemini = None
    Runner = None
    InMemorySessionService = None
    FunctionTool = None
    logger.warning("Google ADK not installed. Install with: pip install google-adk")

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logger.warning("duckduckgo-search not installed. Install with: pip install duckduckgo-search")


AGENT_DESCRIPTION: str = "Financial market analysis and podcast script generation"


def web_search(query: str, max_results: int = 10) -> str:
    """
    Search the web for current information, news, and financial data.
    Use this tool to research market trends, stock prices, company news,
    economic indicators, and other real-time information.
    
    Args:
        query: Search query (be specific and include context)
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        JSON string with search results including titles, URLs, and snippets
    """
    if not DDGS_AVAILABLE:
        return '{"error": "Search tool not available. Please install duckduckgo-search."}'
    
    try:
        results = []
        with DDGS() as ddgs:
            for i, result in enumerate(ddgs.news(query, max_results=max_results)):
                results.append({
                    "type": "news",
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "source": result.get("source", ""),
                })
                if len(results) >= max_results:
                    break
            
            if len(results) < max_results:
                for result in ddgs.text(query, max_results=max_results):
                    url = result.get("href", "")
                    if url and not any(r["url"] == url for r in results):
                        results.append({
                            "type": "web",
                            "title": result.get("title", ""),
                            "url": url,
                            "snippet": result.get("body", ""),
                        })
                        if len(results) >= max_results:
                            break
        
        if not results:
            return '{"results": [], "message": "No results found for: ' + query + '"}'
        
        return '{"results": ' + str(results) + '}'
    
    except Exception as e:
        return '{"error": "Search failed: ' + str(e) + '"}'


def get_search_tool():
    """Get the custom search tool for ADK."""
    if not FunctionTool:
        return None
    return FunctionTool(func=web_search)


def initialize_agent() -> Tuple[Optional["LlmAgent"], Optional["InMemorySessionService"], bool]:
    """
    Initialize Google ADK Agent with model fallback chain.
    
    All models use custom DuckDuckGo web search tool (free, no API key required).

    Returns (agent, session_service, success)
    """
    if not ADK_AVAILABLE:
        logger.error("Google ADK is required. Install: pip install google-adk")
        return None, None, False

    if not DDGS_AVAILABLE:
        logger.warning("duckduckgo-search not installed. Search will be limited.")
        logger.info("Install with: pip install duckduckgo-search")

    search_tool = get_search_tool()
    tools = [search_tool] if search_tool else []

    model_chain = [
        ("gemini-2.5-flash", "gemini"),
        ("gemini-flash-latest", "gemini"),
        ("gemini-2.0-flash", "gemini"),
        ("gemma-4-31b-it", "gemini"),
        ("gemma-4-26b-a4b-it", "gemini"),
    ]

    for model_name, model_type in model_chain:
        try:
            logger.info(f"Initializing agent with model: {model_name}")

            model = Gemini(model=model_name)

            agent = LlmAgent(
                name="podcast_generation_agent",
                model=model,
                description=AGENT_DESCRIPTION,
                instruction=(
                    "You are a financial research agent. "
                    "Research market data and generate professional podcast scripts. "
                    "Use the web_search tool to get current financial news, stock prices, "
                    "market trends, and economic data from the internet."
                ),
                tools=tools,
            )

            session_service = InMemorySessionService()

            logger.info(f"✓ UnifiedAgentService initialized with model: {model_name}")
            return agent, session_service, True

        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            if any(x in error_lower for x in ["429", "rate limit", "quota", "resource exhausted", "too many requests"]):
                logger.warning(f"Model {model_name} rate limited, trying next...")
                continue

            if "not supported" in error_lower or "google search" in error_lower:
                logger.warning(f"Model {model_name} feature issue: {error_msg}, trying next...")
                continue

            logger.error(f"Failed to initialize agent with {model_name}: {error_msg}", exc_info=True)
            continue

    logger.error("All models exhausted - all failed to initialize")
    return None, None, False
