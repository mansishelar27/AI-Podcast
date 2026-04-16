# services/podcast/audio.py
import os
import base64
import io
import wave
import re
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict

from num2words import num2words

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from app.core.config import settings
from app.core.logger import logger

from .ffmpeg_check import PYDUB_AVAILABLE
from .script_splitting import split_podcast_scripts, get_script_chunk

try:
    from pydub import AudioSegment
except ImportError:
    # PYDUB_AVAILABLE is already handled by ffmpeg_check, but we need the import here for types if needed
    pass


INTRO_MUSIC_FALLBACK_PATH = os.path.join(
    str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    "storage",
    "audio",
    "Nippon India Mutual Fund MOGOSCAPE®(2).mp3",
)
IST = ZoneInfo("Asia/Kolkata")
DEBUG_LOG_PATH = "/home/ashishd/AI-Podcast/.cursor/debug-79956e.log"
DEBUG_SESSION_ID = "79956e"


def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: Dict) -> None:
    try:
        payload = {
            "sessionId": DEBUG_SESSION_ID,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(datetime.now().timestamp() * 1000),
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as debug_file:
            debug_file.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass

# Sarvam TTS valid speaker IDs (from API validation). Map legacy/UI names to these.
SARVAM_VALID_SPEAKERS = frozenset({
    "anushka", "abhilash", "manisha", "vidya", "arya", "karun", "hitesh", "arvind",
    "ritu", "priya", "neha", "rahul", "pooja", "rohan", "simran", "kavya", "amit",
    "dev", "ishita", "shreya", "ratan", "varun", "manan", "sumit", "roopa", "kabir",
    "aayan", "shubh", "ashutosh", "advait", "amelia", "sophia", "anand", "tanya", "tarun", "suraj",
})
# Map frontend/legacy voice names to valid Sarvam speaker IDs
SARVAM_SPEAKER_ALIASES = {
    "sachit": "abhilash",   # English male (sachit not in Sarvam list)
    "karan": "karun",     # Hindi male (API uses karun)
}
# Default speakers by language when no valid speaker provided
SARVAM_DEFAULT_SPEAKER = {"en": "abhilash", "hi": "anushka"}


def _resolve_sarvam_speaker(speaker: Optional[str], language: str) -> str:
    """Return a Sarvam-valid speaker ID. Only returns names from SARVAM_VALID_SPEAKERS."""
    raw = (speaker or "").strip().lower()
    if raw in SARVAM_VALID_SPEAKERS:
        return raw
    resolved = SARVAM_SPEAKER_ALIASES.get(raw)
    if resolved and resolved in SARVAM_VALID_SPEAKERS:
        return resolved
    # Any other value (sachit, karan, typo, etc.) -> use language default
    return SARVAM_DEFAULT_SPEAKER.get(language, "anushka")


def _now_ist() -> datetime:
    """Return timezone-aware current datetime in India timezone."""
    return datetime.now(IST)


_HINDI_MONTHS = {
    1: "जनवरी",
    2: "फ़रवरी",
    3: "मार्च",
    4: "अप्रैल",
    5: "मई",
    6: "जून",
    7: "जुलाई",
    8: "अगस्त",
    9: "सितंबर",
    10: "अक्टूबर",
    11: "नवंबर",
    12: "दिसंबर",
}


def _normalize_hindi_dates(text: str) -> str:
    """
    For Hindi scripts, convert ISO dates like 2026-03-01 into a more
    natural Hindi format, e.g. '1 मार्च 2026'. This helps the hi-IN
    TTS model pronounce dates in Hindi instead of reading raw digits
    in an English style.
    """

    def _replace(match: re.Match) -> str:
        year = match.group(1)
        month_num = int(match.group(2))
        day_num = int(match.group(3))
        month_name = _HINDI_MONTHS.get(month_num, match.group(2))
        return f"{day_num} {month_name} {year}"

    return re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", _replace, text)


def _convert_numbers_to_hindi_words(text: str) -> str:
    """
    Convert all standalone integer numbers in text to Hindi words.
    Example:
        2026 -> दो हज़ार छब्बीस
        50   -> पचास
    """

    def replace_number(match: re.Match) -> str:
        number = match.group()
        try:
            # num2words may return hyphenated words; replace hyphen with space
            return num2words(int(number), lang="hi").replace("-", " ")
        except Exception:
            return number  # Fallback: leave as-is if conversion fails

    # Replace standalone integers (not decimals / parts of words)
    return re.sub(r"\b\d+\b", replace_number, text)


def convert_hindi_script_numbers_to_words(script: str) -> str:
    """
    Convert dates and all numbers in a Hindi script to Hindi words.
    Use this for both: (1) script returned in API response (so UI shows
    "एक मार्च दो हज़ार छब्बीस"), and (2) text sent to TTS so it speaks in Hindi.
    """
    script = _normalize_hindi_dates(script)
    script = _convert_numbers_to_hindi_words(script)
    return script


def _combine_wav_chunks_with_wave(chunks_bytes: List[bytes]) -> bytes:
    """
    Combine WAV chunks using Python's wave module (no pydub/ffmpeg).
    Assumes all chunks have same nchannels, sampwidth, framerate.
    """
    if not chunks_bytes:
        return b""
    if len(chunks_bytes) == 1:
        return chunks_bytes[0]
    all_frames = []
    params = None
    for chunk in chunks_bytes:
        with io.BytesIO(chunk) as f:
            with wave.open(f, "rb") as w:
                if params is None:
                    params = w.getparams()
                all_frames.append(w.readframes(w.getnframes()))
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setparams(params)
        w.writeframes(b"".join(all_frames))
    return out.getvalue()


async def combine_wav_chunks(chunks_bytes: List[bytes]) -> bytes:
    """
    Properly combine multiple WAV audio chunks using pydub (or wave fallback).
    Ensures full-length podcast audio instead of only the first chunk (~20s).
    
    Args:
        chunks_bytes: List of WAV audio bytes to combine
    
    Returns:
        Combined WAV audio bytes
    """
    if not chunks_bytes:
        return b""
    if len(chunks_bytes) == 1:
        return chunks_bytes[0]

    if PYDUB_AVAILABLE:
        try:
            combined_audio = AudioSegment.empty()
            for idx, chunk in enumerate(chunks_bytes, 1):
                try:
                    audio_segment = AudioSegment.from_wav(io.BytesIO(chunk))
                    combined_audio += audio_segment
                    logger.debug(f"Combined chunk {idx} ({len(audio_segment)} ms audio)")
                except Exception as e:
                    logger.error(f"Error processing chunk {idx}: {str(e)}")
                    continue
            if not combined_audio:
                logger.error("No audio chunks could be combined")
                return chunks_bytes[0]
            wav_buffer = io.BytesIO()
            combined_audio.export(wav_buffer, format="wav")
            return wav_buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to combine WAV chunks with pydub: {str(e)}")

    # Fallback: combine using wave module so we get FULL audio, not just first chunk
    try:
        combined = _combine_wav_chunks_with_wave(chunks_bytes)
        if combined:
            logger.info("Combined %d WAV chunks using wave module (pydub not used)", len(chunks_bytes))
            return combined
    except Exception as e:
        logger.error(f"Wave fallback failed: {str(e)}")
    return chunks_bytes[0]


async def _prepend_intro_music(audio_bytes: bytes) -> bytes:
    """
    Prepend intro music to the provided audio bytes (WAV format).
    Returns the modified WAV bytes or the original bytes if something fails.
    """
    if not PYDUB_AVAILABLE:
        logger.debug("pydub not available, skipping intro music prepending.")
        return audio_bytes

    try:
        intro_path = _resolve_intro_music_path()
        if not intro_path or not os.path.exists(intro_path):
            logger.debug(f"Intro music file not found at {intro_path}, skipping.")
            return audio_bytes

        logger.info(f"Adding intro music from {intro_path}")
        intro_audio = AudioSegment.from_file(intro_path)
        logger.info(f"Intro audio: {len(intro_audio)} ms, channels={intro_audio.channels}, sample_width={intro_audio.sample_width}, frame_rate={intro_audio.frame_rate}")
        
        # TTS audio from chunks (WAV format from Sarvam/Deepgram)
        tts_audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))
        logger.info(f"TTS audio: {len(tts_audio)} ms, channels={tts_audio.channels}, sample_width={tts_audio.sample_width}, frame_rate={tts_audio.frame_rate}")
        
        # Match TTS audio properties to intro audio (or vice versa)
        if intro_audio.frame_rate != tts_audio.frame_rate:
            tts_audio = tts_audio.set_frame_rate(intro_audio.frame_rate)
        if intro_audio.channels != tts_audio.channels:
            tts_audio = tts_audio.set_channels(intro_audio.channels)
        
        # Prepend intro (simple concatenation)
        final_podcast = intro_audio + tts_audio
        
        # Export back to WAV bytes
        wav_buffer = io.BytesIO()
        final_podcast.export(wav_buffer, format="wav")
        logger.info(f"Intro music prepended successfully ({len(final_podcast)} ms total)")
        return wav_buffer.getvalue()

    except Exception as e:
        logger.error(f"Failed to prepend intro music: {str(e)}")
        return audio_bytes


def _resolve_intro_music_path() -> str:
    """
    Resolve intro music path with an explicit fallback to the requested file.
    """
    configured_path = settings._resolve_intro_music_path()
    if configured_path:
        return configured_path
    if os.path.exists(INTRO_MUSIC_FALLBACK_PATH):
        return INTRO_MUSIC_FALLBACK_PATH
    return ""


async def _prepend_intro_music_mp3(mp3_bytes: bytes) -> bytes:
    """
    Prepend intro music to MP3 bytes and return final MP3 bytes.
    Intro file is already MP3 and is not converted independently.
    """
    if not PYDUB_AVAILABLE:
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H2",
            location="audio.py:_prepend_intro_music_mp3:PYDUB_AVAILABLE",
            message="Skipping intro prepend because pydub unavailable",
            data={"pydub_available": PYDUB_AVAILABLE, "input_bytes": len(mp3_bytes)},
        )
        # endregion
        logger.debug("pydub not available, skipping intro MP3 prepending.")
        return mp3_bytes

    try:
        intro_path = _resolve_intro_music_path()
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H1",
            location="audio.py:_prepend_intro_music_mp3:intro_path_resolved",
            message="Resolved intro path for MP3 prepend",
            data={
                "intro_path": intro_path,
                "intro_exists": bool(intro_path and os.path.exists(intro_path)),
                "input_bytes": len(mp3_bytes),
            },
        )
        # endregion
        if not intro_path:
            logger.debug("Intro music file not found, skipping MP3 intro prepending.")
            return mp3_bytes

        intro_audio = AudioSegment.from_file(intro_path, format="mp3")
        podcast_audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H3",
            location="audio.py:_prepend_intro_music_mp3:loaded_segments",
            message="Loaded intro and podcast segments before concatenation",
            data={
                "intro_ms": len(intro_audio),
                "podcast_ms": len(podcast_audio),
                "intro_frame_rate": intro_audio.frame_rate,
                "podcast_frame_rate": podcast_audio.frame_rate,
                "intro_channels": intro_audio.channels,
                "podcast_channels": podcast_audio.channels,
            },
        )
        # endregion

        # Match generated MP3 properties to intro before concatenation.
        if intro_audio.frame_rate != podcast_audio.frame_rate:
            podcast_audio = podcast_audio.set_frame_rate(intro_audio.frame_rate)
        if intro_audio.channels != podcast_audio.channels:
            podcast_audio = podcast_audio.set_channels(intro_audio.channels)

        final_audio = intro_audio + podcast_audio
        out = io.BytesIO()
        final_audio.export(out, format="mp3", bitrate="192k", parameters=["-q:a", "2"])
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H4",
            location="audio.py:_prepend_intro_music_mp3:exported",
            message="Intro prepend succeeded and exported MP3",
            data={"final_ms": len(final_audio), "output_bytes": out.tell()},
        )
        # endregion
        logger.info("Intro MP3 prepended successfully (%d ms total)", len(final_audio))
        return out.getvalue()
    except Exception as e:
        # region agent log
        _debug_log(
            run_id="pre-fix",
            hypothesis_id="H3",
            location="audio.py:_prepend_intro_music_mp3:exception",
            message="Intro prepend failed with exception",
            data={"error": str(e)},
        )
        # endregion
        logger.error(f"Failed to prepend intro to MP3: {str(e)}")
        return mp3_bytes


async def convert_to_mp3(audio_bytes: bytes) -> bytes:
    """
    Convert audio bytes from WAV to MP3 format.
    
    Args:
        audio_bytes: WAV audio bytes
    
    Returns:
        MP3 audio bytes
    """
    if not PYDUB_AVAILABLE:
        logger.warning("pydub not available. Returning original WAV format.")
        return audio_bytes

    try:
        audio = AudioSegment.from_wav(io.BytesIO(audio_bytes))

        mp3_buffer = io.BytesIO()
        audio.export(
            mp3_buffer,
            format="mp3",
            bitrate="192k",
            parameters=["-q:a", "2"]
        )

        return mp3_buffer.getvalue()

    except Exception as e:
        logger.error(f"MP3 conversion failed: {str(e)}")
        return audio_bytes


async def generate_audio_from_script(
    script: str,
    sarvam_api_key: str,
    tts_url: str,
    language: str = "hi",
    output_format: str = "mp3",
    speaker: Optional[str] = None,
    audio_storage_path: str = settings.AUDIO_STORAGE_PATH,
) -> tuple[Optional[str], Optional[str]]:
    """
    Generate audio from a SINGLE script using Sarvam TTS.
    Splits script into chunks (max 500 chars) and processes each separately.
    Combines all audio chunks into one file.

    Returns:
        (path_to_audio_file, error_message). On success: (path, None). On failure: (None, error_message).
    """
    def fail(msg: str) -> tuple[Optional[str], Optional[str]]:
        return (None, msg)

    if not HTTPX_AVAILABLE:
        logger.error("httpx is not installed. Cannot generate audio.")
        return fail("httpx is not installed. Cannot generate audio.")

    if not sarvam_api_key:
        logger.warning("Sarvam API key not provided. Cannot generate audio.")
        return fail("Sarvam API key not configured. Add SARVAM_API_KEY to .env.")

    target_speaker = _resolve_sarvam_speaker(speaker, language)
    if speaker and target_speaker != (speaker or "").strip().lower():
        logger.info(f"Speaker mapped for Sarvam: {speaker!r} -> {target_speaker!r}")
    logger.info(f"Generating audio from script -> language: {language} | speaker: {target_speaker} | format: {output_format}")

    try:
        # For Hindi, convert dates and numbers to Hindi words so Sarvam
        # speaks them in Hindi (e.g. 2026-03-01 → एक मार्च दो हज़ार छब्बीस).
        if language == "hi":
            script = convert_hindi_script_numbers_to_words(script)

        # Split script into SEPARATE chunks (max 500 chars each)
        from .script_splitting import split_script
        script_chunks = split_script(script, max_length=500, language=language)
        
        logger.info(f"Script split into {len(script_chunks)} SEPARATE chunks for Sarvam TTS")
        all_audio_chunks: List[bytes] = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            for i, chunk in enumerate(script_chunks, 1):
                logger.info(f"Processing chunk {i}/{len(script_chunks)} ({len(chunk)} chars)")

                # Map language code (Sarvam expects hi-IN / en-IN)
                lang_code = "hi-IN" if language == "hi" else "en-IN"

                payload = {
                    "model": "bulbul:v2",
                    "inputs": [chunk],
                    "target_language_code": lang_code,
                    "speaker": target_speaker,
                    "pitch": 1.0,
                    "pace": 1.0,
                    "loudness": 1.5,
                    # Enable Sarvam's smart text preprocessing so numbers and dates
                    # are expanded naturally in the target language (hi-IN / en-IN).
                    # Docs: https://docs.sarvam.ai/.../how-to/enable-text-preprocessing
                    "enable_preprocessing": True,
                }

                headers = {
                    "Authorization": f"Bearer {sarvam_api_key}",
                    "Content-Type": "application/json"
                }

                resp = await client.post(
                    tts_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )

                if resp.status_code != 200:
                    err_snippet = (resp.text or "")[:400]
                    logger.error(f"Sarvam TTS failed for chunk {i}: {resp.status_code} -> {err_snippet}")
                    return fail(f"Sarvam TTS API error ({resp.status_code}): {err_snippet}")

                data = resp.json()
                if "audios" not in data or not data["audios"]:
                    err_detail = data.get("detail") or data.get("message") or resp.text[:200]
                    logger.error(f"No audio returned for chunk {i}: {err_detail}")
                    return fail(f"Sarvam returned no audio: {err_detail}")

                chunk_bytes = base64.b64decode(data["audios"][0])
                all_audio_chunks.append(chunk_bytes)
                logger.debug(f"Chunk {i} audio received ({len(chunk_bytes)} bytes)")

        # Combine all audio chunks
        if not all_audio_chunks:
            logger.error("No audio chunks received")
            return fail("No audio chunks received from TTS.")

        if len(all_audio_chunks) == 1:
            logger.info("Single audio chunk - no combining needed")
            audio_bytes = all_audio_chunks[0]
        else:
            logger.info(f"Combining {len(all_audio_chunks)} audio chunks into one file...")
            audio_bytes = await combine_wav_chunks(all_audio_chunks)

        if not audio_bytes:
            logger.error("Failed to combine audio chunks")
            return fail("Failed to combine audio chunks. (pydub/ffmpeg may be needed for multiple chunks.)")

        # Optional MP3 conversion
        file_extension = "wav"
        if output_format.lower() == "mp3":
            logger.info("Converting WAV to MP3...")
            audio_bytes = await convert_to_mp3(audio_bytes)
            # region agent log
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H4",
                location="audio.py:generate_audio_from_script:before_intro_prepend",
                message="Calling intro prepend for mp3 output",
                data={"language": language, "bytes_before_intro": len(audio_bytes)},
            )
            # endregion
            audio_bytes = await _prepend_intro_music_mp3(audio_bytes)
            # region agent log
            _debug_log(
                run_id="pre-fix",
                hypothesis_id="H4",
                location="audio.py:generate_audio_from_script:after_intro_prepend",
                message="Returned from intro prepend for mp3 output",
                data={"language": language, "bytes_after_intro": len(audio_bytes)},
            )
            # endregion
            file_extension = "mp3"
        else:
            # Keep legacy WAV path intact for non-MP3 output requests.
            audio_bytes = await _prepend_intro_music(audio_bytes)

        # Save file
        timestamp = _now_ist().strftime('%Y%m%d_%H%M%S')
        filename = f"podcast_{language}_{timestamp}.{file_extension}"
        filepath = os.path.join(audio_storage_path, filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        size_mb = len(audio_bytes) / (1024 * 1024)
        logger.info(f"Audio saved -> {filepath} ({size_mb:.2f} MB)")

        return (f"/audio/{filename}", None)

    except Exception as e:
        logger.exception(f"Audio generation failed: {str(e)}")
        return fail(str(e))


async def generate_podcast_audio(
    eng_script: str,
    hin_script: str,
    sarvam_api_key: str,
    tts_url: str,
    output_format: str = "mp3",
    eng_speaker: Optional[str] = None,
    hin_speaker: Optional[str] = None,
    audio_storage_path: str = settings.AUDIO_STORAGE_PATH,
) -> Optional[Dict[str, str]]:
    """
    Generate AUDIO for TWO separate podcast scripts (English and Hindi).
    Each script is split into chunks and processed separately with Sarvam TTS.
    
    IMPORTANT: Does NOT merge scripts. Processes each script independently:
    - English script chunks → English audio file
    - Hindi script chunks → Hindi audio file
    
    Args:
        eng_script: English podcast script
        hin_script: Hindi podcast script
        sarvam_api_key: Sarvam API authentication key
        tts_url: Sarvam TTS API endpoint URL
        output_format: Output audio format ("mp3" or "wav")
        eng_speaker: English speaker name (e.g., "sachit")
        hin_speaker: Hindi speaker name (e.g., "anushka")
        audio_storage_path: Path to save audio files
    
    Returns:
        Dictionary with audio file paths:
        {
            "eng_pod_audio": "/audio/podcast_en_20260226_120000.mp3",
            "hin_pod_audio": "/audio/podcast_hi_20260226_120000.mp3",
            "success": True
        }
        Or None if generation fails
    
    Example:
        result = await generate_podcast_audio(
            eng_script=eng_script,
            hin_script=hin_script,
            sarvam_api_key="your_key",
            tts_url="https://api.sarvam.ai/text-to-speech",
            output_format="mp3"
        )
        
        if result:
            print(f"English audio: {result['eng_pod_audio']}")
            print(f"Hindi audio: {result['hin_pod_audio']}")
    """
    logger.info("=" * 70)
    logger.info("GENERATING PODCAST AUDIO - ENGLISH AND HINDI")
    logger.info("=" * 70)
    
    if not HTTPX_AVAILABLE:
        logger.error("httpx is not installed. Cannot generate audio.")
        return None

    if not sarvam_api_key:
        logger.warning("Sarvam API key not provided. Cannot generate audio.")
        return None

    eng_speaker = eng_speaker or "sachit"
    hin_speaker = hin_speaker or "anushka"

    try:
        # Generate English audio
        logger.info("\n[1/2] GENERATING ENGLISH PODCAST AUDIO (eng_pod)")
        logger.info("-" * 70)
        eng_audio_path, eng_err = await generate_audio_from_script(
            script=eng_script,
            sarvam_api_key=sarvam_api_key,
            tts_url=tts_url,
            language="en",
            output_format=output_format,
            speaker=eng_speaker,
            audio_storage_path=audio_storage_path
        )

        if eng_err or not eng_audio_path:
            logger.error("Failed to generate English audio: %s", eng_err or "unknown")
            return None

        # Generate Hindi audio
        logger.info("\n[2/2] GENERATING HINDI PODCAST AUDIO (hin_pod)")
        logger.info("-" * 70)
        hin_audio_path, hin_err = await generate_audio_from_script(
            script=hin_script,
            sarvam_api_key=sarvam_api_key,
            tts_url=tts_url,
            language="hi",
            output_format=output_format,
            speaker=hin_speaker,
            audio_storage_path=audio_storage_path
        )

        if hin_err or not hin_audio_path:
            logger.error("Failed to generate Hindi audio: %s", hin_err or "unknown")
            return None

        result = {
            "eng_pod_audio": eng_audio_path,
            "hin_pod_audio": hin_audio_path,
            "success": True,
            "format": output_format
        }

        logger.info("\n" + "=" * 70)
        logger.info("✓ PODCAST AUDIO GENERATION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"English audio: {eng_audio_path}")
        logger.info(f"Hindi audio: {hin_audio_path}")
        logger.info("=" * 70 + "\n")

        return result

    except Exception as e:
        logger.exception(f"Podcast audio generation failed: {str(e)}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Deepgram Aura TTS — English audio generation
# Uses Deepgram's Aura model (free tier available).
# No SDK needed — plain HTTP via httpx.
# ─────────────────────────────────────────────────────────────────────────────

# Available Deepgram Aura voices (free tier)
DEEPGRAM_VOICES = {
    # American English — Male
    "aura-arcas-en":   "Male · American · Professional",
    "aura-orion-en":   "Male · American · Natural",
    "aura-zeus-en":    "Male · American · Deep",
    "aura-orpheus-en": "Male · American · Conversational",
    # American English — Female
    "aura-asteria-en": "Female · American · Professional",
    "aura-luna-en":    "Female · American · Warm",
    "aura-stella-en":  "Female · American · Clear",
    # Other English
    "aura-helios-en":  "Male · British",
    "aura-athena-en":  "Female · British",
    "aura-angus-en":   "Male · Irish",
}

# Default: professional American male — good for financial briefings
DEEPGRAM_DEFAULT_VOICE = "aura-arcas-en"

# Deepgram TTS endpoint
DEEPGRAM_TTS_URL = "https://api.deepgram.com/v1/speak"

# Chunk size for Deepgram (larger than Sarvam's 500 — Deepgram handles up to ~2000 chars)
DEEPGRAM_CHUNK_SIZE = 1500


async def generate_english_audio_deepgram(
    script: str,
    deepgram_api_key: str,
    output_format: str = "mp3",
    voice: str = DEEPGRAM_DEFAULT_VOICE,
    audio_storage_path: str = settings.AUDIO_STORAGE_PATH,
) -> tuple[Optional[str], Optional[str]]:
    """
    Generate English audio using Deepgram Aura TTS.

    Replaces Sarvam TTS for English. Hindi continues to use Sarvam.

    Flow:
      1. Split script into ≤1500 char chunks
      2. POST each chunk to Deepgram /v1/speak (returns raw WAV bytes)
      3. Combine WAV chunks with existing combine_wav_chunks()
      4. Optionally convert to MP3 with existing convert_to_mp3()
      5. Save to AUDIO_STORAGE_PATH and return (/audio/filename, None)

    Args:
        script:            English podcast script text
        deepgram_api_key:  Deepgram API key (Token auth)
        output_format:     "mp3" (default) or "wav"
        voice:             Deepgram Aura voice ID (default: aura-arcas-en)
        audio_storage_path: Directory to save the audio file

    Returns:
        (url_path, None)   on success  →  e.g. ("/audio/podcast_en_20260323_120000.mp3", None)
        (None, error_msg)  on failure
    """
    def fail(msg: str) -> tuple[Optional[str], Optional[str]]:
        return (None, msg)

    if not HTTPX_AVAILABLE:
        return fail("httpx is not installed. Cannot call Deepgram API.")

    if not deepgram_api_key:
        return fail("Deepgram API key not configured. Add DEEPGRAM_API_KEY to your .env file.")

    # Validate voice
    if voice not in DEEPGRAM_VOICES:
        logger.warning("Unknown Deepgram voice %r — falling back to %s", voice, DEEPGRAM_DEFAULT_VOICE)
        voice = DEEPGRAM_DEFAULT_VOICE

    logger.info("=" * 60)
    logger.info("DEEPGRAM ENGLISH TTS")
    logger.info("=" * 60)
    logger.info("Voice  : %s (%s)", voice, DEEPGRAM_VOICES[voice])
    logger.info("Format : %s", output_format)
    logger.info("Script : %d chars", len(script))

    try:
        # Split into chunks — Deepgram handles ~2000 chars max per request
        from .script_splitting import split_script
        chunks = split_script(script, max_length=DEEPGRAM_CHUNK_SIZE, language="en")
        logger.info("Split into %d chunk(s) for Deepgram TTS", len(chunks))

        all_audio_chunks: List[bytes] = []

        # Request WAV so we can reuse existing combine_wav_chunks()
        # encoding=linear16 + container=wav → clean WAV bytes
        url = f"{DEEPGRAM_TTS_URL}?model={voice}&encoding=linear16&container=wav"
        headers = {
            "Authorization": f"Token {deepgram_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            for i, chunk in enumerate(chunks, 1):
                logger.info("Deepgram chunk %d/%d (%d chars)", i, len(chunks), len(chunk))

                resp = await client.post(url, headers=headers, json={"text": chunk})

                if resp.status_code != 200:
                    err_snippet = (resp.text or "")[:400]
                    logger.error(
                        "Deepgram TTS failed for chunk %d: HTTP %d → %s",
                        i, resp.status_code, err_snippet,
                    )
                    return fail(
                        f"Deepgram TTS error (HTTP {resp.status_code}): {err_snippet}"
                    )

                # Deepgram returns raw audio bytes (not base64)
                audio_bytes_chunk = resp.content
                if not audio_bytes_chunk:
                    return fail(f"Deepgram returned empty audio for chunk {i}")

                all_audio_chunks.append(audio_bytes_chunk)
                logger.debug("Deepgram chunk %d received (%d bytes)", i, len(audio_bytes_chunk))

        if not all_audio_chunks:
            return fail("No audio chunks received from Deepgram.")

        # Combine WAV chunks using existing helper
        if len(all_audio_chunks) == 1:
            logger.info("Single chunk — no combining needed")
            audio_bytes = all_audio_chunks[0]
        else:
            logger.info("Combining %d Deepgram WAV chunks...", len(all_audio_chunks))
            audio_bytes = await combine_wav_chunks(all_audio_chunks)

        if not audio_bytes:
            return fail("Failed to combine Deepgram audio chunks.")

        # Convert to MP3 if requested
        file_extension = "wav"
        if output_format.lower() == "mp3":
            logger.info("Converting Deepgram WAV → MP3...")
            audio_bytes = await convert_to_mp3(audio_bytes)
            audio_bytes = await _prepend_intro_music_mp3(audio_bytes)
            file_extension = "mp3"
        else:
            audio_bytes = await _prepend_intro_music(audio_bytes)

        # Save to disk
        timestamp = _now_ist().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_en_{timestamp}.{file_extension}"
        filepath = os.path.join(audio_storage_path, filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        size_mb = len(audio_bytes) / (1024 * 1024)
        logger.info("Deepgram English audio saved → %s (%.2f MB)", filepath, size_mb)
        logger.info("=" * 60)

        return (f"/audio/{filename}", None)

    except Exception as exc:
        logger.exception("Deepgram audio generation failed: %s", exc)
        return fail(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Legacy wrapper (kept for backward compatibility)
# ─────────────────────────────────────────────────────────────────────────────

async def generate_audio(
    script: str,
    sarvam_api_key: str,
    tts_url: str,
    language: str = "hi",
    output_format: str = "mp3",
    speaker: Optional[str] = None,
    audio_storage_path: str = settings.AUDIO_STORAGE_PATH,
) -> Optional[str]:
    """
    Legacy function for backward compatibility.
    Use generate_audio_from_script() for new code.

    This function processes a SINGLE script.
    For TWO scripts, use generate_podcast_audio() instead.
    """
    logger.warning("generate_audio() is deprecated. Use generate_audio_from_script() or generate_podcast_audio()")

    path, err = await generate_audio_from_script(
        script=script,
        sarvam_api_key=sarvam_api_key,
        tts_url=tts_url,
        language=language,
        output_format=output_format,
        speaker=speaker,
        audio_storage_path=audio_storage_path,
    )
    return path