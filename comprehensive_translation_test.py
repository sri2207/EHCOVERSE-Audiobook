#!/usr/bin/env python3
"""
Comprehensive test for translation and audio generation
"""

import os
import sys
import logging
import tempfile
import pyttsx3
from deep_translator import GoogleTranslator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_workflow():
    """Test the complete workflow"""
    logger.info("=== Testing complete workflow ===")
    
    # Sample text
    original_text = """Once upon a time, in a quiet village nestled between rolling hills and whispering woods, there lived a young girl named Elena. She had always been curious about the world beyond her small home, dreaming of adventures that awaited in distant lands."""
    
    logger.info("Original text length: %d characters", len(original_text))
    
    # Test translation
    logger.info("🔄 Translating text...")
    try:
        translator = GoogleTranslator(source='auto', target='es')
        translated_text = translator.translate(original_text)
        
        if translated_text:
            logger.info("✅ Translation successful")
            logger.info("Translated text length: %d characters", len(translated_text))
        else:
            logger.error("❌ Translation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Translation error: {e}")
        return False
    
    # Test audio generation
    logger.info("🎙️ Generating audio...")
    try:
        engine = pyttsx3.init()
        
        # Configure engine
        engine.setProperty('rate', 175)
        engine.setProperty('volume', 0.8)
        
        # Generate audio to temporary file
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            engine.save_to_file(translated_text, temp_path)
            engine.runAndWait()
            
            # Check result
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.info(f"✅ Audio file created: {file_size} bytes")
                
                # Read audio data
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                logger.info(f"✅ Audio data size: {len(audio_data)} bytes")
                
                # Clean up
                os.unlink(temp_path)
                logger.info("✅ Temporary file cleaned up")
                return True
            else:
                logger.error("❌ Audio file was not created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Audio generation error: {e}")
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
    """Main test function"""
    logger.info("Starting comprehensive test...")
    
    result = test_workflow()
    
    logger.info("=== FINAL RESULT ===")
    logger.info("Workflow test: %s", "✅ PASS" if result else "❌ FAIL")
    
    if result:
        logger.info("🎉 All components are working correctly!")
    else:
        logger.error("❌ There are issues in the workflow.")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)