import hashlib
import re
import uuid
from typing import Optional, Tuple, List, Set, Any

try:
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from google.adk.runners import Runner
    ADK_RUNNER_AVAILABLE = True
except ImportError:
    ADK_RUNNER_AVAILABLE = False

from app.core.logger import logger


def _fail(msg: str) -> Tuple[None, str, List[str]]:
    """Return (None, error_message, []) for agent failure."""
    return (None, msg, [])


def _extract_urls_from_value(value: Any, seen: Optional[Set[str]] = None) -> Set[str]:
    """Recursively extract http(s) URLs from tool response (dict, list, or string)."""
    if seen is None:
        seen = set()
    if value is None:
        return seen
    if isinstance(value, str):
        for m in re.finditer(r"https?://[^\s\)\]\}\"'\s<>]+", value):
            url = m.group(0).rstrip(".,;:)")
            if len(url) > 10:
                seen.add(url)
        return seen
    if isinstance(value, dict):
        for k, v in value.items():
            if k in ("link", "url", "href", "uri") and isinstance(v, str) and v.startswith("http"):
                seen.add(v)
            else:
                _extract_urls_from_value(v, seen)
        return seen
    if isinstance(value, (list, tuple)):
        for item in value:
            _extract_urls_from_value(item, seen)
        return seen
    return seen


def _text_from_content(content) -> str:
    """Extract plain text from google.genai types.Content, from all parts."""
    if not content:
        return ""
    parts = getattr(content, "parts", None)
    if not parts:
        return ""
    text_parts = []
    for part in parts:
        text = None
        if hasattr(part, "text") and part.text:
            text = part.text
        elif isinstance(part, dict) and part.get("text"):
            text = part["text"]
        if text and isinstance(text, str) and text.strip():
            text_parts.append(text.strip())
    return "\n".join(text_parts) if text_parts else ""


async def run_agent_and_get_script(
    agent,
    session_service,
    prompt: str,
    app_name: str = "podcast_agent"
) -> Tuple[Optional[dict], Optional[str], List[str]]:
    """
    Execute the agent using Runner and collect the final text response and sources.
    Splits the response into eng_pod and hin_pod. Collects URLs from tool (e.g. google_search) responses.
    Returns (scripts_dict, error_message, sources_list).
    """
    if not GENAI_AVAILABLE or not ADK_RUNNER_AVAILABLE:
        logger.error("Google GenAI or ADK Runner not installed. Cannot execute agent.")
        return _fail("Google GenAI or ADK Runner not installed.")

    try:
        # Use unique IDs per request to avoid "Session already exists" on shared server (e.g. Render)
        request_id = uuid.uuid4().hex[:12]
        user_id = f"user_{request_id}"
        session_id = f"session_{request_id}"

        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

        runner = Runner(
            agent=agent,
            app_name=app_name,
            session_service=session_service
        )

        user_content = types.Content(
            role='user',
            parts=[types.Part(text=prompt)]
        )

        all_text_chunks = []
        sources_seen: Set[str] = set()
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content
        ):
            content = getattr(event, "content", None)
            text = _text_from_content(content)
            if text:
                all_text_chunks.append(text)
            # Capture URLs from tool (e.g. google_search) responses via helper and raw parts
            get_responses = getattr(event, "get_function_responses", None)
            if callable(get_responses):
                for fr in get_responses() or []:
                    resp = getattr(fr, "response", None)
                    _extract_urls_from_value(resp, sources_seen)
            # Also inspect content.parts for function_response objects/dicts
            parts = getattr(content, "parts", None)
            if parts:
                for part in parts:
                    fr = getattr(part, "function_response", None)
                    if fr is not None:
                        resp = getattr(fr, "response", None) or getattr(fr, "result", None) or fr
                        _extract_urls_from_value(resp, sources_seen)
                    elif isinstance(part, dict) and part.get("function_response") is not None:
                        fr_dict = part["function_response"]
                        if isinstance(fr_dict, dict):
                            resp = fr_dict.get("response") or fr_dict
                        else:
                            resp = fr_dict
                        _extract_urls_from_value(resp, sources_seen)
        # Use FULL script from ALL streamed chunks (never break early on is_final_response).
        # Breaking on first "final" event was returning only a small tail and caused ~20s audio.
        if all_text_chunks:
            final_response = "\n\n".join(all_text_chunks)
            logger.info("Full script from %d streamed chunks (%d chars)", len(all_text_chunks), len(final_response))
        else:
            final_response = None

        if not final_response or not final_response.strip():
            logger.error("Agent returned no final response text")
            return (None, "The AI agent did not return any transcript. This can happen if the request timed out or the model could not generate content. Please try again.", [])

        logger.info("Agent response received — length: %d chars", len(final_response))

        stripped = final_response.strip()
        scripts = split_podcast_scripts(stripped)

        if not scripts:
            # Fallback: use full response as single script for both (model may have skipped markers)
            min_length = 50
            if len(stripped) >= min_length:
                logger.warning(
                    "No English/Hindi markers found; using full response as both scripts"
                )
                scripts = {"eng_pod": stripped, "hin_pod": stripped}
            else:
                logger.error(
                    "Failed to split response (length %d chars). Need markers or >= %d chars.",
                    len(stripped),
                    min_length,
                )
                return (None, f"The agent response was too short or missing English/Hindi markers ({len(stripped)} chars). Please try again.", [])

        sources_list = sorted(sources_seen)
        if sources_list:
            logger.info("Captured %d source URL(s) from tool responses", len(sources_list))
        logger.info(
            "Successfully split into eng_pod (%d chars) and hin_pod (%d chars)",
            len(scripts["eng_pod"]),
            len(scripts["hin_pod"]),
        )
        return (scripts, None, sources_list)

    except Exception as e:
        logger.error("Runner execution failed: %s", str(e), exc_info=True)
        return _fail(f"Transcript generation failed: {str(e)}")


def split_podcast_scripts(full_response: str) -> Optional[dict]:
    """
    Split the agent response into two separate podcast scripts: English and Hindi.
    Tries exact markers first, then fallback markers (e.g. without leading =).
    
    Returns:
        dict with 'eng_pod' and 'hin_pod' keys, or None if split fails
    """
    # Marker variants (exact first, then lenient)
    marker_pairs = [
        ("=====ENGLISH PODCAST SCRIPT=====", "=====HINDI PODCAST SCRIPT====="),
        ("ENGLISH PODCAST SCRIPT", "HINDI PODCAST SCRIPT"),
        ("English podcast script", "Hindi podcast script"),
        ("## ENGLISH", "## HINDI"),
        ("**ENGLISH SCRIPT**", "**HINDI SCRIPT**"),
        ("ENGLISH SCRIPT:", "HINDI SCRIPT:"),
    ]

    for eng_marker, hin_marker in marker_pairs:
        try:
            eng_start_idx = full_response.find(eng_marker)
            hin_start_idx = full_response.find(hin_marker)

            if eng_start_idx == -1 or hin_start_idx == -1:
                continue

            # English: from end of marker to before Hindi marker
            eng_script = full_response[
                eng_start_idx + len(eng_marker):hin_start_idx
            ].strip()
            # Hindi: from end of marker to end
            hin_script = full_response[
                hin_start_idx + len(hin_marker):
            ].strip()

            # Remove common trailing notes
            for note in ("IMPORTANT:", "Note:", "NOTE:"):
                if note in eng_script:
                    eng_script = eng_script[:eng_script.find(note)].strip()
                if note in hin_script:
                    hin_script = hin_script[:hin_script.find(note)].strip()

            if not eng_script or not hin_script:
                continue

            logger.info(
                "Successfully split podcast scripts into eng_pod and hin_pod"
            )
            return {"eng_pod": eng_script, "hin_pod": hin_script}

        except Exception as e:
            logger.debug(f"Split with markers ({eng_marker!r}, {hin_marker!r}) failed: {e}")
            continue

    logger.error(
        "Could not find English and Hindi script markers in response. "
        "Response length: %d chars",
        len(full_response),
    )
    return None