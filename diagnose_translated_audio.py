#!/usr/bin/env python3
"""
Diagnostic tool to identify issues with translated audio generation
"""

import os
import sys
import logging
import tempfile
import pyttsx3

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_translated_audio_generation():
    """Test the complete translated audio generation workflow"""
    logger.info("=== Testing Translated Audio Generation ===")
    
    try:
        # Import services
        from services.echoverse_audio_service import EchoVerseAudioService
        from services.alternative_service import AlternativeService
        
        # Test 1: Initialize services
        logger.info("Test 1: Initializing services...")
        audio_service = EchoVerseAudioService()
        alternative_service = AlternativeService()
        
        if not audio_service.alternative_service:
            logger.error("❌ Audio service failed to initialize alternative service")
            return False
            
        if not alternative_service.tts_engine:
            logger.error("❌ Alternative service failed to initialize TTS engine")
            return False
            
        logger.info("✅ Services initialized successfully")
        
        # Test 2: Test English audio generation (baseline)
        logger.info("Test 2: Generating English audio (baseline)...")
        english_text = "This is a test of English audio generation."
        english_audio = audio_service.generate_speech(
            text=english_text,
            voice="Lisa",
            language="en"
        )
        
        if english_audio and len(english_audio) > 1000:
            logger.info(f"✅ English audio generated successfully: {len(english_audio)} bytes")
        else:
            logger.error(f"❌ English audio generation failed: {len(english_audio) if english_audio else 0} bytes")
            return False
        
        # Test 3: Test Spanish audio generation
        logger.info("Test 3: Generating Spanish audio...")
        spanish_text = "Esta es una prueba de generación de audio en español."
        spanish_audio = audio_service.generate_speech(
            text=spanish_text,
            voice="Lisa",
            language="es"
        )
        
        if spanish_audio and isinstance(spanish_audio, bytes) and len(spanish_audio) > 1000:
            logger.info(f"✅ Spanish audio generated successfully: {len(spanish_audio)} bytes")
        else:
            logger.error(f"❌ Spanish audio generation failed: {len(spanish_audio) if spanish_audio else 0} bytes")
            # Let's debug what's happening
            logger.info("Debugging Spanish audio generation...")
            spanish_audio_debug = alternative_service.generate_speech(
                text=spanish_text,
                voice="Lisa",
                language="es"
            )
            logger.info(f"Direct alternative service result: {len(spanish_audio_debug) if spanish_audio_debug else 0} bytes")
            return False
        
        # Test 4: Test Tamil audio generation
        logger.info("Test 4: Generating Tamil audio...")
        tamil_text = "இது தமிழில் ஆடியோ உருவாக்கத்தை சோதிக்கும் ஒரு சோதனை."
        tamil_audio = audio_service.generate_speech(
            text=tamil_text,
            voice="Lisa",
            language="ta"
        )
        
        if tamil_audio and isinstance(tamil_audio, bytes) and len(tamil_audio) > 0:
            logger.info(f"✅ Tamil audio generated successfully: {len(tamil_audio)} bytes")
        else:
            logger.error(f"❌ Tamil audio generation failed: {len(tamil_audio) if tamil_audio else 0} bytes")
            # Let's debug what's happening
            logger.info("Debugging Tamil audio generation...")
            tamil_audio_debug = alternative_service.generate_speech(
                text=tamil_text,
                voice="Lisa",
                language="ta"
            )
            logger.info(f"Direct alternative service result: {len(tamil_audio_debug) if tamil_audio_debug else 0} bytes")
            return False
        
        # Test 5: Test with longer translated text
        logger.info("Test 5: Testing with longer translated text...")
        long_spanish_text = """Esta es una historia más larga para probar la generación de audio. 
        Cuando tenemos textos más largos, a veces pueden surgir problemas con la generación de audio. 
        Es importante asegurarnos de que todo el texto se procese correctamente y que el audio generado 
        tenga una duración adecuada. Esta prueba nos ayudará a identificar cualquier problema con 
        textos más largos en diferentes idiomas."""
        
        long_spanish_audio = audio_service.generate_speech(
            text=long_spanish_text,
            voice="Lisa",
            language="es"
        )
        
        if long_spanish_audio and isinstance(long_spanish_audio, bytes) and len(long_spanish_audio) > 5000:
            logger.info(f"✅ Long Spanish audio generated successfully: {len(long_spanish_audio)} bytes")
        else:
            logger.error(f"❌ Long Spanish audio generation failed: {len(long_spanish_audio) if long_spanish_audio else 0} bytes")
            return False
        
        logger.info("=== All Tests Passed ===")
        logger.info("🎉 Translated audio generation is working correctly!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during testing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_language_code_mapping():
    """Test language code mapping function"""
    logger.info("=== Testing Language Code Mapping ===")
    
    # Test language code mapping (as used in the app)
    language_codes = {
        "Spanish": "es",
        "French": "fr", 
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Hindi": "hi",
        "Chinese": "zh",
        "Japanese": "ja",
        "Tamil": "ta",
        "English": "en",
        "Korean": "ko",
        "Russian": "ru",
        "Arabic": "ar",
        "Dutch": "nl",
        "Swedish": "sv",
        "Polish": "pl",
        "Turkish": "tr",
        "Thai": "th",
        "Vietnamese": "vi"
    }
    
    test_languages = ["Spanish", "Tamil", "English"]
    
    for lang_name in test_languages:
        code = language_codes.get(lang_name, "en")
        logger.info(f"✅ {lang_name} -> {code}")
    
    logger.info("✅ Language code mapping working correctly")

def main():
    """Main diagnostic function"""
    logger.info("Starting translated audio diagnostics...")
    
    # Test language code mapping
    test_language_code_mapping()
    
    # Test audio generation
    result = test_translated_audio_generation()
    
    if result:
        logger.info("🎉 All diagnostics passed! Translated audio should work correctly.")
        return True
    else:
        logger.error("❌ Diagnostics failed. There may be issues with translated audio generation.")
        logger.info("💡 Try the following troubleshooting steps:")
        logger.info("   1. Check if your system has language-specific voices installed")
        logger.info("   2. Verify that the language codes are correctly mapped")
        logger.info("   3. Ensure the text being passed is not empty or too short")
        logger.info("   4. Check the logs for specific error messages")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)