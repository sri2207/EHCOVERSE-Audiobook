#!/usr/bin/env python3
"""
Test script to verify the audio service fix
"""

import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_audio_service():
    """Test the audio service with fallback TTS"""
    try:
        from services.echoverse_audio_service import EchoVerseAudioService
        
        # Initialize the service
        audio_service = EchoVerseAudioService()
        
        # Test with a simple text
        test_text = "Hello, this is a test of the fallback text-to-speech engine."
        
        logger.info("Testing fallback TTS generation...")
        audio_data = audio_service.generate_speech(test_text, voice="Lisa")
        
        if audio_data and isinstance(audio_data, bytes):
            logger.info(f"✅ Success! Generated {len(audio_data)} bytes of audio data")
            
            # Save to file for verification
            with open("test_output.wav", "wb") as f:
                f.write(audio_data)
            logger.info("💾 Audio saved to test_output.wav")
            return True
        else:
            logger.error("❌ Failed to generate audio data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing audio service: {e}")
        return False