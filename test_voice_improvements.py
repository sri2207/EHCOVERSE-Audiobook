#!/usr/bin/env python3
"""
Test voice improvements and language handling
"""

import os
import sys
import logging
import tempfile
import pyttsx3
from typing import Optional, Sized, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_len(obj: Any) -> int:
    """Safely get the length of an object, returning 0 if it's None or not sized"""
    if obj is None:
        return 0
    if isinstance(obj, (str, list, tuple, dict, bytes)) or hasattr(obj, '__len__'):
        return len(obj)
    return 0

def test_language_voice_mapping():
    """Test language-specific voice mapping"""
    logger.info("=== Testing language voice mapping ===")
    
    try:
        # Import the alternative service
        from services.alternative_service import AlternativeService
        service = AlternativeService()
        
        if not service.tts_engine:
            logger.error("❌ TTS engine not initialized")
            return False
            
        # Get available voices
        voices = service.tts_engine.getProperty('voices')
        logger.info(f"Found {safe_len(voices)} voices")
        
        # Test voice mapping for different languages
        test_cases = [
            ("Lisa", "en", "English test"),
            ("Lisa", "es", "Prueba en español"),
            ("Lisa", "ta", "தமிழ் சோதனை"),  # Tamil
        ]
        
        for voice, language, text in test_cases:
            logger.info(f"Testing voice='{voice}', language='{language}'")
            voice_id = service._map_voice_to_system(voice, voices, language)
            logger.info(f"  Mapped to: {voice_id}")
            
            # Test actual audio generation
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                if voice_id:
                    service.tts_engine.setProperty('voice', voice_id)
                
                service.tts_engine.setProperty('rate', 150)
                service.tts_engine.setProperty('volume', 0.8)
                
                service.tts_engine.save_to_file(text, temp_path)
                service.tts_engine.runAndWait()
                
                if os.path.exists(temp_path):
                    file_size = os.path.getsize(temp_path)
                    logger.info(f"  ✅ Generated audio: {file_size} bytes")
                    os.unlink(temp_path)
                else:
                    logger.error(f"  ❌ Failed to generate audio")
                    
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in language voice mapping test: {e}")
        return False

def test_full_workflow():
    """Test the full workflow with language parameter"""
    logger.info("=== Testing full workflow ===")
    
    try:
        from services.echoverse_audio_service import EchoVerseAudioService
        audio_service = EchoVerseAudioService()
        
        # Test English text
        english_text = "This is a test of the English voice."
        english_audio = audio_service.generate_speech(
            text=english_text,
            voice="Lisa",
            language="en"
        )
        
        if english_audio:
            logger.info(f"✅ English audio generated: {safe_len(english_audio)} bytes")
        else:
            logger.error("❌ Failed to generate English audio")
            return False
        
        # Test Spanish text
        spanish_text = "Esta es una prueba de la voz en español."
        spanish_audio = audio_service.generate_speech(
            text=spanish_text,
            voice="Lisa",
            language="es"
        )
        
        if spanish_audio:
            logger.info(f"✅ Spanish audio generated: {safe_len(spanish_audio)} bytes")
        else:
            logger.error("❌ Failed to generate Spanish audio")
            return False
        
        # Test Tamil text
        tamil_text = "இது தமிழில் குரலை சோதிக்கும் ஒரு சோதனை."
        tamil_audio = audio_service.generate_speech(
            text=tamil_text,
            voice="Lisa",
            language="ta"
        )
        
        if tamil_audio:
            logger.info(f"✅ Tamil audio generated: {safe_len(tamil_audio)} bytes")
        else:
            logger.error("❌ Failed to generate Tamil audio")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in full workflow test: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting voice improvements test...")
    
    # Test language voice mapping
    test1_result = test_language_voice_mapping()
    
    # Test full workflow
    test2_result = test_full_workflow()
    
    logger.info("=== FINAL RESULTS ===")
    logger.info(f"Language voice mapping: {'✅ PASS' if test1_result else '❌ FAIL'}")
    logger.info(f"Full workflow: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    overall_result = test1_result and test2_result
    logger.info(f"Overall: {'✅ PASS' if overall_result else '❌ FAIL'}")
    
    if overall_result:
        logger.info("🎉 All voice improvements are working correctly!")
    else:
        logger.error("❌ There are issues with voice improvements.")
    
    return overall_result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)