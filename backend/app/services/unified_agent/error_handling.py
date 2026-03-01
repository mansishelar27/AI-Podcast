from typing import Dict, Any


def error_response(message: str) -> Dict[str, Any]:
    return {
        "podcast_script": f"Error generating podcast: {message}",
        "success": False,
        "error": message,
        "script_length": 0
    }