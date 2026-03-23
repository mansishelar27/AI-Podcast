import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logger import logger
from app.services.unified_agent.service import unified_agent_service
from app.services.podcast.service import podcast_service
from app.services.podcast.script_splitting import split_podcast_scripts, validate_script_chunks
from app.services.podcast.audio import convert_hindi_script_numbers_to_words
from app.services.cloudinary_service import upload_mp3


class OrchestratorService:
    """
    Main orchestration service for podcast generation.
    
    Workflow:
    1. Generate podcast scripts (English + Hindi) using agent
    2. Split scripts into chunks for Sarvam TTS
    3. Generate audio based on selected language:
       - "en" → English audio only
       - "hi" → Hindi audio only
       - "both" → Both English and Hindi audio
    4. Return results with generated scripts and audio files
    """

    async def generate_podcast(
        self,
        name: str,
        voice_agent: Optional[str] = None,
        language: str = "both",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration pipeline for podcast generation.
        
        Args:
            name: Podcast name/attribution (e.g., "Nippon India Financial")
            voice_agent: Speaker/voice name (e.g., "sachit" for English, "anushka" for Hindi)
            language: Target language for audio generation
                     - "en": English audio only
                     - "hi": Hindi audio only
                     - "both": Both English and Hindi audio (default)
        
        Returns:
            Dictionary with generated podcast scripts and audio paths:
            {
                "status": "success",
                "date": "2026-02-26",
                "name": "Nippon India Financial",
                "language": "en",
                "scripts": {
                    "eng_pod": "...",
                    "hin_pod": "..."
                },
                "script_lengths": {
                    "eng_pod": 1500,
                    "hin_pod": 1600
                },
                "audio": {
                    "eng_pod_audio": "/audio/podcast_en_20260226_120000.mp3",
                    "hin_pod_audio": "/audio/podcast_hi_20260226_120000.mp3"
                },
                "speaker": "sachit",
                "chunks": {
                    "eng_pod_count": 3,
                    "hin_pod_count": 3
                },
                "error": None
            }
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        try:
            # Validate language parameter
            if language not in ["en", "hi", "both"]:
                logger.error(f"Invalid language: {language}. Must be 'en', 'hi', or 'both'")
                return self._error_response(
                    f"Invalid language: {language}. Use 'en', 'hi', or 'both'",
                    yesterday,
                    name,
                    language
                )

            logger.info("=" * 70)
            logger.info("STARTING PODCAST GENERATION ORCHESTRATION")
            logger.info("=" * 70)
            logger.info(f"Name: {name}")
            logger.info(f"Voice Agent: {voice_agent or 'default'}")
            logger.info(f"Language: {language}")
            logger.info(f"Date: {yesterday}")
            logger.info("=" * 70)

            # ===== STEP 1: GENERATE SCRIPTS =====
            logger.info("\n[STEP 1/4] GENERATING PODCAST SCRIPTS")
            logger.info("-" * 70)
            logger.info(f"Using unified agent to generate English and Hindi scripts...")

            scripts_result = await unified_agent_service.process_podcast_request(
                target_date=yesterday,
                attribution=name,
                custom_prompt=custom_prompt
            )

            if not scripts_result.get("success"):
                error_msg = scripts_result.get("error", "Agent failed")
                logger.error(f"Script generation failed: {error_msg}")
                return self._error_response(error_msg, yesterday, name, language)

            # Extract scripts and sources
            eng_script = scripts_result.get("eng_pod", "")
            hin_script = scripts_result.get("hin_pod", "")
            sources_used = scripts_result.get("sources_used") or []

            if not eng_script or not hin_script:
                error_msg = "Agent did not return both English and Hindi scripts"
                logger.error(error_msg)
                return self._error_response(error_msg, yesterday, name, language)

            logger.info(f"✓ English script generated: {len(eng_script)} characters")
            logger.info(f"✓ Hindi script generated: {len(hin_script)} characters")

            # Save raw data for audit
            logger.info("\nSaving raw data for audit...")
            self._save_raw_data(scripts_result, yesterday, name)
            logger.info("✓ Raw data saved")

            # ===== STEP 2: SPLIT SCRIPTS INTO CHUNKS =====
            logger.info("\n[STEP 2/4] SPLITTING SCRIPTS INTO CHUNKS")
            logger.info("-" * 70)
            logger.info("Splitting both scripts into chunks for Sarvam TTS (max 500 chars)...")

            chunks = split_podcast_scripts(
                eng_script=eng_script,
                hin_script=hin_script,
                max_length=500
            )

            if not validate_script_chunks(chunks):
                error_msg = "Script chunk validation failed"
                logger.error(error_msg)
                return self._error_response(error_msg, yesterday, name, language)

            logger.info(f"✓ English chunks: {chunks['eng_pod_count']}")
            logger.info(f"✓ Hindi chunks: {chunks['hin_pod_count']}")

            # ===== STEP 3: GENERATE AUDIO BASED ON LANGUAGE =====
            logger.info("\n[STEP 3/4] GENERATING PODCAST AUDIO")
            logger.info("-" * 70)

            audio_result = None
            audio_paths = {}

            if language == "en":
                # Generate English audio only (bulbul:v2: abhilash)
                logger.info("Generating English audio only...")
                
                eng_speaker = voice_agent or "abhilash"
                eng_audio_path, eng_err = await podcast_service.generate_audio_from_script(
                    script=eng_script,
                    sarvam_api_key=settings.SARVAM_API_KEY,
                    tts_url="https://api.sarvam.ai/text-to-speech",
                    language="en",
                    output_format="mp3",
                    speaker=eng_speaker
                )

                if not eng_audio_path:
                    error_msg = eng_err or "Failed to generate English audio"
                    logger.error(error_msg)
                    return self._error_response(error_msg, yesterday, name, language)

                audio_paths = {
                    "eng_pod_audio": eng_audio_path,
                    "hin_pod_audio": None
                }
                logger.info("English audio generated: %s", eng_audio_path)

            elif language == "hi":
                # Generate Hindi audio only (free-tier: anushka)
                logger.info("Generating Hindi audio only...")
                
                hin_speaker = voice_agent or "anushka"
                hin_audio_path, hin_err = await podcast_service.generate_audio_from_script(
                    script=hin_script,
                    sarvam_api_key=settings.SARVAM_API_KEY,
                    tts_url="https://api.sarvam.ai/text-to-speech",
                    language="hi",
                    output_format="mp3",
                    speaker=hin_speaker
                )

                if not hin_audio_path:
                    error_msg = hin_err or "Failed to generate Hindi audio"
                    logger.error(error_msg)
                    return self._error_response(error_msg, yesterday, name, language)

                audio_paths = {
                    "eng_pod_audio": None,
                    "hin_pod_audio": hin_audio_path
                }
                logger.info("Hindi audio generated: %s", hin_audio_path)

            else:  # language == "both"
                # Generate both English and Hindi audio (bulbul:v2 speakers only)
                logger.info("Generating both English and Hindi audio...")
                voice = (voice_agent or "").strip().lower()
                eng_default, hin_default = "abhilash", "anushka"
                hindi_capable = {"anushka", "karun", "manisha", "vidya", "arya"}
                if voice in hindi_capable:
                    eng_speaker = eng_default
                    hin_speaker = voice_agent or hin_default
                else:
                    eng_speaker = voice_agent or eng_default
                    hin_speaker = hin_default

                audio_result = await podcast_service.generate_podcast_audio(
                    eng_script=eng_script,
                    hin_script=hin_script,
                    sarvam_api_key=settings.SARVAM_API_KEY,
                    tts_url="https://api.sarvam.ai/text-to-speech",
                    output_format="mp3",
                    eng_speaker=eng_speaker,
                    hin_speaker=hin_speaker
                )

                if not audio_result or not audio_result.get("success"):
                    error_msg = "Failed to generate audio"
                    logger.error(error_msg)
                    return self._error_response(error_msg, yesterday, name, language)

                audio_paths = {
                    "eng_pod_audio": audio_result.get("eng_pod_audio"),
                    "hin_pod_audio": audio_result.get("hin_pod_audio")
                }
                logger.info(f"✓ English audio: {audio_paths['eng_pod_audio']}")
                logger.info(f"✓ Hindi audio: {audio_paths['hin_pod_audio']}")

            # ===== STEP 3b: UPLOAD TO CLOUDINARY (optional, non-fatal) =====
            try:
                logger.info("\n[STEP 3b] UPLOADING AUDIO TO CLOUDINARY")
                logger.info("-" * 70)
                audio_paths = self._upload_audio_paths_to_cloudinary(audio_paths, name, yesterday)
            except Exception as cloud_err:
                logger.warning("Cloudinary upload failed (using local paths): %s", cloud_err)

            # ===== STEP 4: COMPILE RESULTS =====
            logger.info("\n[STEP 4/4] COMPILING RESULTS")
            logger.info("-" * 70)

            # Hindi script: return version with numbers/dates as Hindi words
            # so UI shows "एक मार्च दो हज़ार छब्बीस" and TTS speaks the same
            hin_pod_for_response = convert_hindi_script_numbers_to_words(hin_script)

            result = {
                "status": "success",
                "date": yesterday,
                "name": name,
                "attribution": name,
                "language": language,
                "scripts": {
                    "eng_pod": eng_script,
                    "hin_pod": hin_pod_for_response
                },
                "script_lengths": {
                    "eng_pod": len(eng_script),
                    "hin_pod": len(hin_pod_for_response),
                    "total": len(eng_script) + len(hin_pod_for_response)
                },
                "audio": audio_paths,
                "speaker": voice_agent or ("abhilash" if language == "en" else "anushka"),
                "chunks": {
                    "eng_pod_count": chunks['eng_pod_count'],
                    "hin_pod_count": chunks['hin_pod_count'],
                    "total": chunks['total_chunks']
                },
                "error": None,
                "sources_used": sources_used,
                "timestamp": datetime.now().isoformat()
            }

            logger.info("\n" + "=" * 70)
            logger.info("✓ PODCAST GENERATION COMPLETE")
            logger.info("=" * 70)
            logger.info(f"Status: Success")
            logger.info(f"Language: {language}")
            
            if language == "en" or language == "both":
                logger.info(f"English Audio: {audio_paths['eng_pod_audio']}")
            
            if language == "hi" or language == "both":
                logger.info(f"Hindi Audio: {audio_paths['hin_pod_audio']}")
            
            logger.info("=" * 70 + "\n")

            return result

        except Exception as e:
            logger.exception(f"Orchestrator pipeline failed: {str(e)}")
            return self._error_response(str(e), yesterday, name, language)

    def _upload_audio_paths_to_cloudinary(
        self,
        audio_paths: Dict[str, Optional[str]],
        podcast_name: str,
        date_str: str,
    ) -> Dict[str, Optional[str]]:
        """Upload local audio files to Cloudinary via upload_mp3(); return dict with Cloudinary URLs or original paths."""
        result = {}
        for key in ("eng_pod_audio", "hin_pod_audio"):
            path = audio_paths.get(key)
            if not path:
                result[key] = None
                continue
            filename = os.path.basename(path)
            local_path = os.path.join(settings.AUDIO_STORAGE_PATH, filename)
            if not os.path.isfile(local_path):
                logger.warning("Local file not found for upload: %s", local_path)
                result[key] = path
                continue
            try:
                public_id = f"podcasts/{filename.replace('.mp3', '')}"
                resp = upload_mp3(local_path, public_id=public_id)
                url = resp.get("secure_url") or resp.get("url")
                result[key] = url if url else path
            except Exception as e:
                logger.warning("Cloudinary upload failed for %s: %s", filename, e)
                result[key] = path
        return result

    def _save_raw_data(self, data: Any, date_str: str, podcast_name: str):
        """Save raw generated data for audit and debugging"""
        try:
            timestamp = datetime.now().strftime('%H%M%S')
            filename = f"raw_{podcast_name}_{date_str}_{timestamp}.json"
            filepath = os.path.join(settings.RAW_DATA_STORAGE_PATH, filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Raw data saved: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save raw data: {str(e)}")

    def _error_response(
        self,
        error_msg: str,
        date: str,
        name: str,
        language: str = "both"
    ) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            "status": "error",
            "date": date,
            "name": name,
            "language": language,
            "scripts": {
                "eng_pod": None,
                "hin_pod": None
            },
            "audio": {
                "eng_pod_audio": None,
                "hin_pod_audio": None
            },
            "error": error_msg,
            "sources_used": [],
            "timestamp": datetime.now().isoformat()
        }


# Global instance
orchestrator_service = OrchestratorService()