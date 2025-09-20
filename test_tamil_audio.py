#!/usr/bin/env python3
"""
Test script for Tamil audio generation with improved quality
"""

import os
import sys
import logging
from typing import Optional

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tamil_audio_generation():
    """Test Tamil audio generation with the improved implementation"""
    try:
        logger.info("Testing Tamil audio generation...")
        
        # Import the alternative service
        from services.alternative_service import AlternativeService
        service = AlternativeService()
        
        # Test Tamil text
        tamil_text = "இது தமிழில் ஒரு எடுத்துக்காட்டு உரை. இந்த உரை தமிழ் எழுத்துகளை சரியாக ஒலிபரப்ப உதவும்."
        
        logger.info(f"Input text: {tamil_text}")
        logger.info(f"Text length: {len(tamil_text)} characters")
        
        # Generate Tamil audio
        tamil_audio = service.generate_speech(
            text=tamil_text,
            voice="Lisa",
            language="ta",
            audio_format="audio/mp3"
        )
        
        if tamil_audio:
            audio_size = len(tamil_audio)
            logger.info(f"✅ Successfully generated Tamil audio: {audio_size} bytes")
            
            # Save the audio to a file for verification
            output_file = "tamil_test_audio.mp3"
            with open(output_file, "wb") as f:
                f.write(tamil_audio)
            
            logger.info(f"✅ Tamil audio saved to {output_file}")
            
            # Provide audio details
            size_kb = round(audio_size / 1024, 2)
            estimated_duration = round(audio_size / 16000, 2)  # Rough estimate
            
            print("\n" + "="*50)
            print("TAMIL AUDIO DETAILS")
            print("="*50)
            print(f"File: {output_file}")
            print(f"Size: {audio_size} bytes ({size_kb} KB)")
            print(f"Estimated Duration: {estimated_duration} seconds")
            print(f"Language: Tamil (ta)")
            print(f"Voice: Lisa")
            print(f"Format: MP3")
            print("="*50)
            
            return True
        else:
            logger.error("❌ Failed to generate Tamil audio")
            return False
            
    except Exception as e:
        logger.error(f"Error in Tamil audio generation test: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting Tamil audio generation test...")
    
    success = test_tamil_audio_generation()
    
    if success:
        logger.info("🎉 Tamil audio generation test completed successfully!")
        return 0
    else:
        logger.error("❌ Tamil audio generation test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())