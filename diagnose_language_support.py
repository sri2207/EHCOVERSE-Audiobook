#!/usr/bin/env python3
"""
Diagnostic tool to check language support for TTS engines
"""

import os
import sys
import logging
import pyttsx3
from typing import List, Any, cast

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_voices() -> List[Any]:
    """Check what voices are available on the system"""
    logger.info("=== Checking System Voices ===")
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        if not voices:
            logger.warning("No voices found on the system")
            engine.stop()
            return []
        
        # Convert voices to a list we can work with
        voices_list: List[Any] = []
        
        # Handle voices as an iterable object
        # Try the most common cases first
        if isinstance(voices, (list, tuple)):
            voices_list = list(voices)
        else:
            # Try to iterate over voices using hasattr checks
            if hasattr(voices, '__iter__'):
                try:
                    # Cast to make type checker happy
                    iterable_voices = cast(Any, voices)
                    for voice in iterable_voices:
                        voices_list.append(voice)
                except Exception:
                    pass
            elif hasattr(voices, '__len__') and hasattr(voices, '__getitem__'):
                # Handle it as a sequence
                try:
                    # Cast to make type checker happy
                    sequence_voices = cast(Any, voices)
                    length = len(sequence_voices)
                    for i in range(length):
                        try:
                            voice = sequence_voices[i]
                            voices_list.append(voice)
                        except (IndexError, TypeError):
                            # Skip if we can't access this index
                            continue
                except Exception:
                    pass
            else:
                # Try to handle it as a single object
                # Check if it has attributes of a voice object
                if hasattr(voices, 'id') or hasattr(voices, 'name'):
                    voices_list.append(voices)
        
        logger.info("Found %d voices:", len(voices_list))
        for i, voice in enumerate(voices_list):
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = getattr(voice, 'name', 'Unknown')
            voice_languages = getattr(voice, 'languages', [])
            logger.info("  %d. ID: %s", i+1, voice_id)
            logger.info("      Name: %s", voice_name)
            logger.info("      Languages: %s", voice_languages)
            logger.info("")
        
        engine.stop()
        return voices_list
        
    except Exception as e:
        logger.error("Error checking system voices: %s", e)
        return []

def test_language_support(voices: List[Any], language_code: str, language_name: str, sample_text: str) -> bool:
    """Test if a specific language is supported"""
    logger.info("=== Testing %s (%s) Support ===", language_name, language_code)
    
    if not voices:
        logger.error("No voices available to test")
        return False
    
    # Language-specific voice preferences
    language_voice_prefs = {
        "es": ["spanish", "es"],
        "fr": ["french", "fr"],
        "de": ["german", "de"],
        "it": ["italian", "it"],
        "pt": ["portuguese", "pt"],
        "hi": ["hindi", "hi"],
        "zh": ["chinese", "zh"],
        "ja": ["japanese", "ja"],
        "ta": ["tamil", "ta"],
        "en": ["english", "en", "microsoft"]
    }
    
    language_prefs = language_voice_prefs.get(language_code, [language_code])
    logger.info("Looking for voices with preferences: %s", language_prefs)
    
    # Find matching voices
    matching_voices: List[Any] = []
    for voice in voices:
        voice_id = getattr(voice, 'id', str(voice))
        voice_name = voice_id.lower()
        
        language_match = any(lang_pref in voice_name for lang_pref in language_prefs)
        if language_match:
            matching_voices.append(voice)
            logger.info("Found matching voice: %s", voice_id)
    
    if not matching_voices:
        logger.warning("No voices found that match %s preferences", language_name)
        return False
    
    logger.info("Found %d voices that might support %s", len(matching_voices), language_name)
    return True

def main() -> bool:
    """Main diagnostic function"""
    logger.info("Starting language support diagnostics...")
    
    # Check system voices
    voices = check_system_voices()
    
    # Test specific languages
    languages_to_test = [
        ("en", "English", "This is a test of English text to speech."),
        ("es", "Spanish", "Esta es una prueba de texto a voz en español."),
        ("ta", "Tamil", "இது தமிழில் பேச்சு உரை சோதனை."),
        ("fr", "French", "Ceci est un test de synthèse vocale en français."),
        ("zh", "Chinese", "这是中文语音合成测试。")
    ]
    
    results = {}
    for lang_code, lang_name, sample_text in languages_to_test:
        result = test_language_support(voices, lang_code, lang_name, sample_text)
        results[lang_name] = result
        logger.info("")
    
    # Summary
    logger.info("=== Summary ===")
    supported_languages = [lang for lang, supported in results.items() if supported]
    unsupported_languages = [lang for lang, supported in results.items() if not supported]
    
    if supported_languages:
        logger.info("✅ Supported languages: %s", ', '.join(supported_languages))
    else:
        logger.info("✅ No specific language support detected (may still work with default voices)")
    
    if unsupported_languages:
        logger.info("⚠️  Languages that may have limited support: %s", ', '.join(unsupported_languages))
        logger.info("💡 For better support, consider installing language-specific voice packages")
    
    logger.info("🎉 Language support diagnostics completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)