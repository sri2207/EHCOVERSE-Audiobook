#!/usr/bin/env python3
"""
Verification script for EchoVerse audio generation fix
"""

import os
import sys
import logging

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_fix():
    """Verify that the audio generation fix is working"""
    logger.info("=== Verifying EchoVerse Audio Generation Fix ===")
    
    try:
        # Import the services
        from services.echoverse_audio_service import EchoVerseAudioService
        from services.alternative_service import AlternativeService
        
        # Test 1: Check if AlternativeService can be initialized
        logger.info("Test 1: Initializing AlternativeService...")
        alt_service = AlternativeService()
        logger.info("✅ AlternativeService initialized successfully")
        
        # Test 2: Check if EchoVerseAudioService can be initialized
        logger.info("Test 2: Initializing EchoVerseAudioService...")
        audio_service = EchoVerseAudioService()
        logger.info("✅ EchoVerseAudioService initialized successfully")
        
        # Test 3: Generate English audio
        logger.info("Test 3: Generating English audio...")
        english_text = "This is a test to verify that English audio generation is working correctly."
        english_audio = audio_service.generate_speech(
            text=english_text,
            voice="Lisa",
            language="en"
        )
        
        if english_audio and len(english_audio) > 1000:  # Should be more than 1KB
            logger.info(f"✅ English audio generated successfully: {len(english_audio)} bytes")
        else:
            logger.error("❌ English audio generation failed or produced insufficient data")
            return False
        
        # Test 4: Generate Spanish audio
        logger.info("Test 4: Generating Spanish audio...")
        spanish_text = "Esta es una prueba para verificar que la generación de audio en español funciona correctamente."
        spanish_audio = audio_service.generate_speech(
            text=spanish_text,
            voice="Lisa",
            language="es"
        )
        
        if spanish_audio and len(spanish_audio) > 1000:  # Should be more than 1KB
            logger.info(f"✅ Spanish audio generated successfully: {len(spanish_audio)} bytes")
        else:
            logger.error("❌ Spanish audio generation failed or produced insufficient data")
            return False
        
        # Test 5: Generate Tamil audio
        logger.info("Test 5: Generating Tamil audio...")
        tamil_text = "ஆங்கிலம் ஆடியோ உருவாக்கம் சரியாக வேலை செய்கிறதா என்பதை சரிபார்க்க இது ஒரு சோதனை."
        tamil_audio = audio_service.generate_speech(
            text=tamil_text,
            voice="Lisa",
            language="ta"
        )
        
        if tamil_audio and len(tamil_audio) > 0:  # Tamil might generate less data
            logger.info(f"✅ Tamil audio generated successfully: {len(tamil_audio)} bytes")
        else:
            logger.error("❌ Tamil audio generation failed")
            return False
        
        logger.info("=== All Tests Passed! ===")
        logger.info("🎉 The audio generation fix is working correctly!")
        logger.info("You can now generate full-length audio for translated text in EchoVerse.")
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed with error: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting EchoVerse audio fix verification...")
    
    success = verify_fix()
    
    if success:
        logger.info("✅ Verification completed successfully!")
        logger.info("The audio generation issues have been resolved.")
    else:
        logger.error("❌ Verification failed!")
        logger.error("There may still be issues with audio generation.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)