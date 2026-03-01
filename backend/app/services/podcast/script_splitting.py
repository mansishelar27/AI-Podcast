import re
from typing import List, Dict, Optional

from app.core.logger import logger


def split_script(script: str, max_length: int = 500, language: str = "en") -> List[str]:
    """
    Split long script into chunks of max_length characters.
    Splits at sentence boundaries to keep sentences intact.
    Supports both English and Hindi.
    
    IMPORTANT: Chunks are kept SEPARATE for Sarvam TTS processing.
    Each chunk will be sent separately to TTS API (max 500 characters per chunk).
    Do NOT combine or merge chunks.
    
    Args:
        script: Script text to split
        max_length: Maximum characters per chunk (default 500)
        language: 'en' for English or 'hi' for Hindi
    
    Returns:
        List of SEPARATE script chunks (each <= max_length characters)
    """
    if len(script) <= max_length:
        logger.info(f"Script length: {len(script)} chars (within limit)")
        return [script]

    logger.info(f"Script length: {len(script)} chars - splitting into chunks of max {max_length} chars (language: {language})")

    chunks = []
    current_chunk = ""

    # Use different sentence delimiters based on language
    if language == "hi":
        # Hindi sentence delimiters: Devanagari Danda (।) and Double Danda (॥)
        sentence_pattern = r'(?<=[.!?।॥])\s+'
    else:
        # English sentence delimiters: Period, Exclamation, Question
        sentence_pattern = r'(?<=[.!?])\s+'

    # Split by sentence delimiters, keeping the delimiter
    sentences = re.split(sentence_pattern, script)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if current_chunk and len(current_chunk) + len(sentence) + 1 > max_length:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    logger.info(f"✅ Split into {len(chunks)} SEPARATE chunks (for Sarvam TTS processing):")
    for idx, chunk in enumerate(chunks, 1):
        logger.info(f"   Chunk {idx}: {len(chunk)} characters (ready for TTS)")

    return chunks


def split_podcast_scripts(
    eng_script: str,
    hin_script: str,
    max_length: int = 500
) -> Dict[str, any]:
    """
    Split both English and Hindi podcast scripts into SEPARATE chunks.
    Each chunk is kept independent for Sarvam TTS processing.
    
    CRITICAL: Do NOT combine or merge chunks. Each chunk will be sent 
    separately to Sarvam TTS API with maximum 500 characters per API call.
    
    Args:
        eng_script: English podcast script
        hin_script: Hindi podcast script (Devanagari)
        max_length: Maximum characters per chunk (default 500 - Sarvam TTS limit)
    
    Returns:
        Dictionary containing:
        {
            "eng_pod_chunks": [chunk1, chunk2, chunk3, ...] - SEPARATE chunks,
            "hin_pod_chunks": [chunk1, chunk2, chunk3, ...] - SEPARATE chunks,
            "eng_pod_count": number of English chunks,
            "hin_pod_count": number of Hindi chunks,
            "total_chunks": total chunks (eng + hin),
            "eng_pod_total_chars": total chars in English script,
            "hin_pod_total_chars": total chars in Hindi script
        }
    
    Example:
        result = split_podcast_scripts(eng_script, hin_script, max_length=500)
        
        # Process each chunk SEPARATELY with Sarvam TTS
        for chunk in result["eng_pod_chunks"]:
            audio = sarvam_tts.convert(chunk, language="en")
            # Save audio...
    """
    logger.info("=" * 70)
    logger.info("SPLITTING PODCAST SCRIPTS - ENGLISH AND HINDI")
    logger.info("IMPORTANT: Chunks will be kept SEPARATE for Sarvam TTS")
    logger.info("=" * 70)
    
    # Split English script
    logger.info("\n[1/2] SPLITTING ENGLISH PODCAST SCRIPT (eng_pod)")
    logger.info("-" * 70)
    eng_chunks = split_script(eng_script, max_length, language="en")
    
    # Split Hindi script
    logger.info("\n[2/2] SPLITTING HINDI PODCAST SCRIPT (hin_pod)")
    logger.info("-" * 70)
    hin_chunks = split_script(hin_script, max_length, language="hi")
    
    # Compile results
    result = {
        "eng_pod_chunks": eng_chunks,
        "hin_pod_chunks": hin_chunks,
        "eng_pod_count": len(eng_chunks),
        "hin_pod_count": len(hin_chunks),
        "total_chunks": len(eng_chunks) + len(hin_chunks),
        "eng_pod_total_chars": len(eng_script),
        "hin_pod_total_chars": len(hin_script)
    }
    
    # Log summary
    logger.info("\n" + "=" * 70)
    logger.info("SPLIT SUMMARY - CHUNKS READY FOR SARVAM TTS")
    logger.info("=" * 70)
    logger.info(f"English Script (eng_pod):")
    logger.info(f"  Total Characters: {result['eng_pod_total_chars']}")
    logger.info(f"  SEPARATE Chunks: {result['eng_pod_count']}")
    for idx, chunk in enumerate(eng_chunks, 1):
        logger.info(f"    Chunk {idx}: {len(chunk)} chars")
    
    logger.info(f"\nHindi Script (hin_pod):")
    logger.info(f"  Total Characters: {result['hin_pod_total_chars']}")
    logger.info(f"  SEPARATE Chunks: {result['hin_pod_count']}")
    for idx, chunk in enumerate(hin_chunks, 1):
        logger.info(f"    Chunk {idx}: {len(chunk)} chars")
    
    logger.info(f"\nTotal SEPARATE Chunks: {result['total_chunks']}")
    logger.info("NOTE: Each chunk will be sent separately to Sarvam TTS API")
    logger.info("=" * 70 + "\n")
    
    return result


def get_script_chunk(
    scripts_dict: Dict[str, any],
    language: str = "en",
    chunk_index: int = 0
) -> Optional[str]:
    """
    Retrieve a SINGLE chunk for Sarvam TTS processing.
    This chunk will be sent as-is to the TTS API (max 500 characters).
    
    Args:
        scripts_dict: Dictionary returned from split_podcast_scripts()
        language: 'en' for English, 'hi' for Hindi
        chunk_index: Zero-based index of chunk to retrieve
    
    Returns:
        SINGLE script chunk string (ready for TTS), or None if chunk doesn't exist
    
    Example:
        # Get each chunk and send to Sarvam TTS separately
        result = split_podcast_scripts(eng_script, hin_script)
        
        for i in range(result["eng_pod_count"]):
            chunk = get_script_chunk(result, language="en", chunk_index=i)
            audio = sarvam_tts.convert(chunk, language="en")  # Send chunk as-is
            # Save audio file...
    """
    if language == "en":
        chunks = scripts_dict.get("eng_pod_chunks", [])
        lang_name = "English (eng_pod)"
    elif language == "hi":
        chunks = scripts_dict.get("hin_pod_chunks", [])
        lang_name = "Hindi (hin_pod)"
    else:
        logger.error(f"Invalid language: {language}. Use 'en' or 'hi'")
        return None
    
    if chunk_index < 0 or chunk_index >= len(chunks):
        logger.error(f"Chunk index {chunk_index} out of range for {lang_name} (valid: 0-{len(chunks)-1})")
        return None
    
    chunk = chunks[chunk_index]
    logger.info(f"✓ Retrieved {lang_name} chunk {chunk_index + 1}/{len(chunks)} ({len(chunk)} chars) - Ready for Sarvam TTS")
    return chunk


def validate_script_chunks(scripts_dict: Dict[str, any]) -> bool:
    """
    Validate that both English and Hindi scripts are properly split into SEPARATE chunks.
    Checks:
    - All required keys present
    - Chunks exist and are non-empty
    - Each chunk is within Sarvam TTS limit (500 characters max)
    - Chunk counts match declared counts
    
    Args:
        scripts_dict: Dictionary returned from split_podcast_scripts()
    
    Returns:
        True if valid, False otherwise
    
    Example:
        chunks = split_podcast_scripts(eng_script, hin_script)
        if validate_script_chunks(chunks):
            print("✓ All chunks valid for Sarvam TTS")
        else:
            print("✗ Validation failed")
    """
    try:
        logger.info("Validating script chunks for Sarvam TTS...")
        
        # Check required keys
        required_keys = [
            "eng_pod_chunks", "hin_pod_chunks", 
            "eng_pod_count", "hin_pod_count",
            "total_chunks"
        ]
        
        for key in required_keys:
            if key not in scripts_dict:
                logger.error(f"✗ Missing required key: {key}")
                return False
        
        # Check English chunks
        eng_chunks = scripts_dict.get("eng_pod_chunks", [])
        eng_count = scripts_dict.get("eng_pod_count", 0)
        
        if not eng_chunks:
            logger.error("✗ No English chunks found")
            return False
        
        if len(eng_chunks) != eng_count:
            logger.error(f"✗ English chunk count mismatch: {len(eng_chunks)} chunks vs {eng_count} declared")
            return False
        
        # Validate each English chunk
        sarvam_max = 500
        for i, chunk in enumerate(eng_chunks):
            if not chunk or not chunk.strip():
                logger.error(f"✗ English chunk {i} is empty")
                return False
            
            chunk_len = len(chunk)
            if chunk_len > sarvam_max:
                logger.error(f"✗ English chunk {i} is too large: {chunk_len} chars (max: {sarvam_max})")
                return False
        
        # Check Hindi chunks
        hin_chunks = scripts_dict.get("hin_pod_chunks", [])
        hin_count = scripts_dict.get("hin_pod_count", 0)
        
        if not hin_chunks:
            logger.error("✗ No Hindi chunks found")
            return False
        
        if len(hin_chunks) != hin_count:
            logger.error(f"✗ Hindi chunk count mismatch: {len(hin_chunks)} chunks vs {hin_count} declared")
            return False
        
        # Validate each Hindi chunk
        for i, chunk in enumerate(hin_chunks):
            if not chunk or not chunk.strip():
                logger.error(f"✗ Hindi chunk {i} is empty")
                return False
            
            chunk_len = len(chunk)
            if chunk_len > sarvam_max:
                logger.error(f"✗ Hindi chunk {i} is too large: {chunk_len} chars (max: {sarvam_max})")
                return False
        
        logger.info(f"✓ Validation passed: All chunks valid for Sarvam TTS")
        logger.info(f"  - English: {eng_count} chunks (all ≤ 500 chars)")
        logger.info(f"  - Hindi: {hin_count} chunks (all ≤ 500 chars)")
        return True
    
    except Exception as e:
        logger.error(f"✗ Error validating script chunks: {str(e)}")
        return False


def get_chunk_info(scripts_dict: Dict[str, any]) -> Dict[str, any]:
    """
    Get detailed information about script chunks for monitoring.
    Shows size of each chunk for Sarvam TTS processing.
    
    Args:
        scripts_dict: Dictionary returned from split_podcast_scripts()
    
    Returns:
        Dictionary with detailed chunk information
    
    Example:
        chunks = split_podcast_scripts(eng_script, hin_script)
        info = get_chunk_info(chunks)
        
        # Check if all chunks fit within Sarvam TTS limit
        if all(size <= 500 for size in info["eng_pod"]["chunk_sizes"]):
            print("✓ All English chunks fit Sarvam limit")
    """
    eng_chunks = scripts_dict.get("eng_pod_chunks", [])
    hin_chunks = scripts_dict.get("hin_pod_chunks", [])
    
    eng_sizes = [len(chunk) for chunk in eng_chunks]
    hin_sizes = [len(chunk) for chunk in hin_chunks]
    
    info = {
        "eng_pod": {
            "total_chunks": len(eng_chunks),
            "total_chars": scripts_dict.get("eng_pod_total_chars", 0),
            "chunk_sizes": eng_sizes,
            "avg_chunk_size": sum(eng_sizes) / len(eng_sizes) if eng_sizes else 0,
            "min_chunk_size": min(eng_sizes) if eng_sizes else 0,
            "max_chunk_size": max(eng_sizes) if eng_sizes else 0,
            "sarvam_compatible": all(size <= 500 for size in eng_sizes)
        },
        "hin_pod": {
            "total_chunks": len(hin_chunks),
            "total_chars": scripts_dict.get("hin_pod_total_chars", 0),
            "chunk_sizes": hin_sizes,
            "avg_chunk_size": sum(hin_sizes) / len(hin_sizes) if hin_sizes else 0,
            "min_chunk_size": min(hin_sizes) if hin_sizes else 0,
            "max_chunk_size": max(hin_sizes) if hin_sizes else 0,
            "sarvam_compatible": all(size <= 500 for size in hin_sizes)
        },
        "total_chunks": scripts_dict.get("total_chunks", 0)
    }
    
    logger.info("Chunk Information Summary (for Sarvam TTS):")
    logger.info(f"  English: {info['eng_pod']['total_chunks']} chunks " + 
                f"(avg: {info['eng_pod']['avg_chunk_size']:.0f} chars, " +
                f"max: {info['eng_pod']['max_chunk_size']} chars)")
    logger.info(f"  Hindi: {info['hin_pod']['total_chunks']} chunks " +
                f"(avg: {info['hin_pod']['avg_chunk_size']:.0f} chars, " +
                f"max: {info['hin_pod']['max_chunk_size']} chars)")
    logger.info(f"  ✓ English Sarvam compatible: {info['eng_pod']['sarvam_compatible']}")
    logger.info(f"  ✓ Hindi Sarvam compatible: {info['hin_pod']['sarvam_compatible']}")
    
    return info