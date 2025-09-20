import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_integration():
    """Test the full EchoVerse integration with audio generation"""
    try:
        # Initialize services
        from services.ibm_watson_service import IBMWatsonService
        from services.echoverse_audio_service import EchoVerseAudioService
        
        logger.info("Initializing Watson service...")
        watson_service = IBMWatsonService()
        
        logger.info("Initializing EchoVerse audio service...")
        audio_service = EchoVerseAudioService()
        
        # Test text
        test_text = "Welcome to EchoVerse, an AI-powered audiobook creation tool. This is a test of our fallback text-to-speech engine."
        
        logger.info("Testing audio generation with fallback TTS...")
        audio_data = audio_service.generate_speech(test_text, voice="Lisa")
        
        if audio_data and isinstance(audio_data, bytes):
            logger.info(f"✅ Success! Generated {len(audio_data)} bytes of audio")
            
            # Save the audio file
            with open("integration_test_output.wav", "wb") as f:
                f.write(audio_data)
            logger.info("💾 Audio saved to integration_test_output.wav")
            
            # Test voice mapping
            logger.info("Testing different voices...")
            voices_to_test = ["Michael", "Allison"]
            for voice in voices_to_test:
                voice_audio = audio_service.generate_speech(
                    f"This is a test of the {voice} voice.", 
                    voice=voice
                )
                if voice_audio and isinstance(voice_audio, bytes):
                    logger.info(f"✅ {voice} voice working: {len(voice_audio)} bytes")
                else:
                    logger.warning(f"❌ {voice} voice failed")
            
            return True
        else:
            logger.error("❌ Failed to generate audio")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in full integration test: {e}")
        return False

def main():
    """Run the integration test"""
    logger.info("Starting full integration test...")
    
    result = test_full_integration()
    
    if result:
        logger.info("🎉 Full integration test completed successfully!")
    else:
        logger.error("❌ Full integration test failed!")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)