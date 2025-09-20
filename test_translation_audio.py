#!/usr/bin/env python3
"""
Test translation and audio generation workflow
"""

import logging
import sys
import os
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_translation_and_audio():
    """Test the full translation and audio generation workflow"""
    try:
        from services.alternative_service import AlternativeService
        from deep_translator import GoogleTranslator
        import pyttsx3
        
        logger.info("Initializing services...")
        alternative_service = AlternativeService()
        translator = GoogleTranslator(source='en', target='es')
        
        if not alternative_service.tts_engine:
            logger.error("❌ TTS engine not available")
            return False
            
        # Test text
        english_text = "Hello, this is a test of the translation and audio generation workflow."
        logger.info(f"Original English text: {english_text}")
        
        # Translate text
        logger.info("Translating text to Spanish...")
        translated_text = translator.translate(english_text)
        logger.info(f"Translated Spanish text: {translated_text}")
        
        if not translated_text:
            logger.error("❌ Translation failed")
            return False
        
        # Generate audio using pyttsx3 directly first
        logger.info("Testing direct pyttsx3 audio generation...")
        engine = pyttsx3.init()
        
        # Generate audio with default voice
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            engine.save_to_file(translated_text, temp_path)
            engine.runAndWait()
            
            # Check if file was created
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.info(f"✅ Translated audio file created: {file_size} bytes")
                
                # Read audio data
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                if audio_data and isinstance(audio_data, bytes):
                    logger.info(f"✅ Audio data: {len(audio_data)} bytes")
                else:
                    logger.error("❌ Failed to read audio data")
                    return False
                
                # Clean up
                os.unlink(temp_path)
                logger.info("✅ Temporary file cleaned up")
                return True
            else:
                logger.error("❌ Audio file was not created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during audio generation: {e}")
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            return False
            
    except Exception as e:
        logger.error(f"❌ Audio generation error: {e}")
        return False

def main():
    """Run the translation and audio test"""
    logger.info("Starting translation and audio test...")
    
    result = test_translation_and_audio()
    
    if result:
        logger.info("🎉 Translation and audio test completed successfully!")
    else:
        logger.error("❌ Translation and audio test failed!")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)