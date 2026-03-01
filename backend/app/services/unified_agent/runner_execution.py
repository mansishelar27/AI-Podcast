import hashlib
from typing import Optional, Tuple

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


def _fail(msg: str) -> Tuple[None, str]:
    """Return (None, error_message) for agent failure."""
    return (None, msg)


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
) -> Optional[dict]:
    """
    Execute the agent using Runner and collect the final text response.
    Splits the response into two separate files: eng_pod (English) and hin_pod (Hindi).
    Returns a dictionary with both scripts.
    """
    if not GENAI_AVAILABLE or not ADK_RUNNER_AVAILABLE:
        logger.error("Google GenAI or ADK Runner not installed. Cannot execute agent.")
        return None

    try:
        user_id = f"user_{hashlib.md5(prompt.encode()).hexdigest()[:8]}"
        session_id = f"session_{hashlib.md5(prompt.encode()).hexdigest()[:10]}"

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
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content
        ):
            text = _text_from_content(getattr(event, "content", None))
            if text:
                all_text_chunks.append(text)
        # Use FULL script from ALL streamed chunks (never break early on is_final_response).
        # Breaking on first "final" event was returning only a small tail and caused ~20s audio.
        if all_text_chunks:
            final_response = "\n\n".join(all_text_chunks)
            logger.info("Full script from %d streamed chunks (%d chars)", len(all_text_chunks), len(final_response))
        else:
            final_response = None

        if not final_response or not final_response.strip():
            logger.error("Agent returned no final response text")
            return _fail("The AI agent did not return any transcript. This can happen if the request timed out or the model could not generate content. Please try again.")

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
                return _fail(
                    f"The agent response was too short or missing English/Hindi markers ({len(stripped)} chars). Please try again."
                )

        logger.info(
            "Successfully split into eng_pod (%d chars) and hin_pod (%d chars)",
            len(scripts["eng_pod"]),
            len(scripts["hin_pod"]),
        )
        return (scripts, None)

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