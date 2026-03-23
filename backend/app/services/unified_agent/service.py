import socket
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.logger import logger

from .agent_init import initialize_agent, ADK_AVAILABLE
from .prompt_builder import build_podcast_prompt
from .runner_execution import run_agent_and_get_script
from .script_cleaner import clean_generated_script
from .error_handling import error_response


def _agent_not_ready_message() -> str:
    """Return a user-facing message explaining why the agent is not available."""
    if not ADK_AVAILABLE:
        return (
            "Google ADK is not installed or could not be loaded. "
            "Install with: pip install google-adk (in the backend venv)."
        )
    if not settings.GEMINI_API_KEY:
        return (
            "Gemini API key is not configured. "
            "Add GEMINI_API_KEY to a .env file in the backend folder or set the environment variable. "
            "Get a key at: https://aistudio.google.com/apikey"
        )
    return "Agent or session service not initialized."


class UnifiedAgentService:
    def __init__(self):
        self.agent = None
        self.session_service = None
        self.app_name = "podcast_agent"

        if ADK_AVAILABLE:
            self.agent, self.session_service, success = initialize_agent()
            if not success:
                logger.error("UnifiedAgentService failed to initialize properly")

    async def process_podcast_request(
        self,
        target_date: Optional[str] = None,
        attribution: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: generate financial podcast scripts (English and Hindi) using Google ADK agent.
        Returns two separate podcast scripts: eng_pod (English) and hin_pod (Hindi).
        If custom_prompt is provided (session-only), it overrides the default from prompt_builder.
        """
        target_date = target_date or "yesterday"
        attribution = attribution or "Financial Research Team"

        if not self.agent or not self.session_service:
            return error_response(_agent_not_ready_message())

        try:
            logger.info(f"Starting podcast script generation for date: {target_date}")
            if custom_prompt:
                logger.info("Using custom prompt (session-only) for this request")

            prompt = custom_prompt if custom_prompt else build_podcast_prompt(target_date, attribution)

            # Run agent and get dictionary with both scripts and sources
            scripts_dict, agent_error, sources_used = await run_agent_and_get_script(
                agent=self.agent,
                session_service=self.session_service,
                prompt=prompt,
                app_name=self.app_name
            )

            if not scripts_dict:
                return error_response(
                    agent_error or "No valid response received from agent"
                )

            # Validate that we have both scripts
            if "eng_pod" not in scripts_dict or "hin_pod" not in scripts_dict:
                logger.error("Agent response missing eng_pod or hin_pod")
                return error_response("Invalid response format - missing eng_pod or hin_pod")

            # Extract and clean both scripts
            eng_pod_raw = scripts_dict.get("eng_pod", "")
            hin_pod_raw = scripts_dict.get("hin_pod", "")

            # Clean both scripts
            eng_pod_cleaned = clean_generated_script(eng_pod_raw)
            hin_pod_cleaned = clean_generated_script(hin_pod_raw)

            # Validate both scripts have sufficient content
            min_length = 300
            if len(eng_pod_cleaned) < min_length:
                logger.warning(f"English script too short: {len(eng_pod_cleaned)} chars")
                return error_response(f"English script too short ({len(eng_pod_cleaned)} chars)")

            if len(hin_pod_cleaned) < min_length:
                logger.warning(f"Hindi script too short: {len(hin_pod_cleaned)} chars")
                return error_response(f"Hindi script too short ({len(hin_pod_cleaned)} chars)")

            logger.info(
                f"✓ Podcast scripts generated successfully — "
                f"eng_pod: {len(eng_pod_cleaned)} chars, "
                f"hin_pod: {len(hin_pod_cleaned)} chars"
            )

            return {
                "eng_pod": eng_pod_cleaned,
                "hin_pod": hin_pod_cleaned,
                "success": True,
                "attribution": attribution,
                "date": target_date,
                "eng_pod_length": len(eng_pod_cleaned),
                "hin_pod_length": len(hin_pod_cleaned),
                "total_length": len(eng_pod_cleaned) + len(hin_pod_cleaned),
                "scripts_generated": 2,
                "sources_used": sources_used or [],
            }

        except (socket.gaierror, OSError) as e:
            errno = getattr(e, "errno", None)
            if errno == 11001 or errno == -2 or "getaddrinfo failed" in str(e):
                msg = (
                    "Network/DNS error: Cannot reach Google APIs. "
                    "Check: (1) Internet connection, (2) DNS (try 8.8.8.8), "
                    "(3) Firewall/proxy, (4) VPN if on corporate network."
                )
                logger.error("%s [%s]", msg, e)
                return error_response(msg)
            logger.error(f"Network error in podcast generation: {e}", exc_info=True)
            return error_response(f"Network error: {e}")
        except Exception as e:
            logger.error(f"Critical error in podcast generation: {str(e)}", exc_info=True)
            return error_response(str(e))

    async def process_podcast_request_for_tts(
        self,
        target_date: Optional[str] = None,
        attribution: Optional[str] = None,
        return_format: str = "dict"
    ) -> Dict[str, Any]:
        """
        Generate podcast scripts and return in format suitable for TTS processing.
        
        Args:
            target_date: Target date for financial updates
            attribution: Podcast attribution/name
            return_format: 'dict' for Python dict, 'json' for JSON-serializable format
        
        Returns:
            Dictionary with eng_pod and hin_pod ready for Sarvam TTS
        """
        result = await self.process_podcast_request(target_date, attribution)

        if not result.get("success"):
            return result

        # Format for TTS processing
        tts_ready_response = {
            "status": "success",
            "eng_pod": {
                "language": "en",
                "content": result.get("eng_pod"),
                "length_chars": result.get("eng_pod_length"),
                "ready_for_tts": True
            },
            "hin_pod": {
                "language": "hi",
                "content": result.get("hin_pod"),
                "length_chars": result.get("hin_pod_length"),
                "ready_for_tts": True
            },
            "metadata": {
                "attribution": result.get("attribution"),
                "date": result.get("date"),
                "total_scripts": 2,
                "total_characters": result.get("total_length")
            }
        }

        logger.info("Podcast scripts formatted and ready for TTS processing")
        return tts_ready_response


# Global instance
unified_agent_service = UnifiedAgentService()