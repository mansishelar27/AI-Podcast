import re

from app.core.logger import logger


def clean_generated_script(raw_script: str) -> str:
    """
    Remove markdown artifacts and normalize whitespace for clean TTS input.
    """
    if not raw_script:
        return ""

    try:
        # Headers
        script = re.sub(r'^#+\s+', '', raw_script, flags=re.MULTILINE)

        # Bold / italic
        script = re.sub(r'\*\*(.+?)\*\*', r'\1', script)
        script = re.sub(r'\*(.+?)\*', r'\1', script)
        script = re.sub(r'__(.+?)__', r'\1', script)
        script = re.sub(r'_(.+?)_', r'\1', script)

        # Code blocks & inline code
        script = re.sub(r'```[\s\S]*?```', '', script)
        script = re.sub(r'`([^`]+)`', r'\1', script)

        # Lists
        script = re.sub(r'^\s*[-*+]\s+', '', script, flags=re.MULTILINE)
        script = re.sub(r'^\s*\d+\.\s+', '', script, flags=re.MULTILINE)

        # Collapse multiple newlines
        script = re.sub(r'\n\n+', '\n\n', script)

        # Trim
        script = script.strip()

        logger.info(f"Script cleaned — final length: {len(script)} chars")
        return script

    except Exception as e:
        logger.warning(f"Script cleaning failed: {str(e)} — returning original")
        return raw_script