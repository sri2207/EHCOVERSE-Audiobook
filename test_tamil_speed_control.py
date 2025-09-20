#!/usr/bin/env python3
"""
Test script for Tamil TTS with speed control
"""

import os
import sys
import logging

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tamil_speed_control():
    """Test Tamil TTS with different speed settings"""
    try:
        logger.info("Testing Tamil TTS with speed control...")
        
        # Import the alternative service
        from services.alternative_service import AlternativeService
        service = AlternativeService()
        
        # Test Tamil text
        text = "இது தமிழில் ஒரு எடுத்துக்காட்டு உரை. தமிழ் எழுத்துகளை சரியாக ஒலிபரப்ப உதவும்."
        logger.info(f"Input text: {text}")
        logger.info(f"Text length: {len(text)} characters")
        
        # Test different speeds
        speeds = ["slow", "normal", "fast"]
        
        for speed in speeds:
            logger.info(f"\n--- Testing speed: {speed} ---")
            
            # Generate Tamil audio with specific speed
            tamil_audio = service.generate_speech_with_speed(
                text=text,
                voice="Lisa",
                language="ta",
                speed=speed
            )
            
            if tamil_audio:
                audio_size = len(tamil_audio)
                logger.info(f"✅ Successfully generated Tamil audio with {speed} speed: {audio_size} bytes")
                
                # Save the audio to a file for verification
                filename = f"tamil_test_{speed}_speed.mp3"
                with open(filename, "wb") as f:
                    f.write(tamil_audio)
                
                logger.info(f"✅ Tamil audio saved to {filename}")
            else:
                logger.error(f"❌ Failed to generate Tamil audio with {speed} speed")
        
        logger.info("\n🎉 Speed control test completed!")
        return True
            
    except Exception as e:
        logger.error(f"Error in Tamil speed control test: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting Tamil TTS speed control test...")
    
    success = test_tamil_speed_control()
    
    if success:
        logger.info("🎉 Tamil TTS speed control test completed successfully!")
        return 0
    else:
        logger.error("❌ Tamil TTS speed control test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())