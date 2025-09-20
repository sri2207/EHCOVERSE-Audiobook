#!/usr/bin/env python3
"""
Enhanced test script for Tamil TTS with quality assessment
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def assess_audio_quality(audio_data: bytes, text: str) -> Dict[str, Any]:
    """Assess the quality of generated audio"""
    if not audio_data:
        return {'quality': 'none', 'size': 0, 'duration_estimate': 0}
    
    size = len(audio_data)
    # Rough estimate: 16000 bytes per second for good quality audio
    duration_estimate = size / 16000.0
    
    # Quality assessment based on size
    if size > 50000:  # More than 50KB
        quality = 'excellent'
    elif size > 20000:  # More than 20KB
        quality = 'good'
    elif size > 5000:   # More than 5KB
        quality = 'acceptable'
    elif size > 1000:   # More than 1KB
        quality = 'poor'
    else:
        quality = 'very_poor'
    
    return {
        'quality': quality,
        'size': size,
        'size_kb': round(size / 1024, 2),
        'duration_estimate': round(duration_estimate, 2)
    }

def test_enhanced_tamil_tts():
    """Test enhanced Tamil TTS with quality assessment"""
    try:
        logger.info("Testing enhanced Tamil TTS...")
        
        # Import the alternative service
        from services.alternative_service import AlternativeService
        service = AlternativeService()
        
        # Test Tamil texts of varying complexity
        test_cases = [
            {
                'name': 'Simple Sentence',
                'text': 'இது தமிழில் ஒரு எடுத்துக்காட்டு உரை.'
            },
            {
                'name': 'Complex Sentence',
                'text': 'இந்த உரை தமிழ் எழுத்துகளை சரியாக ஒலிபரப்ப உதவும். தமிழ் மொழியின் சிறப்பு இதில் தெளிவாக விளங்கும்.'
            },
            {
                'name': 'With Punctuation',
                'text': 'தமிழில் எழுதுவது எப்படி? அது மிகவும் எளிதானது! நீங்கள் முயற்சி செய்தால், உங்களால் முடியும்.'
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            name = test_case['name']
            text = test_case['text']
            
            logger.info(f"\n--- Testing: {name} ---")
            logger.info(f"Input text: {text}")
            logger.info(f"Text length: {len(text)} characters")
            
            # Generate Tamil audio
            tamil_audio = service.generate_speech(
                text=text,
                voice="Lisa",
                language="ta",
                audio_format="audio/mp3"
            )
            
            # Assess quality
            quality_info = assess_audio_quality(tamil_audio, text)
            
            if tamil_audio:
                audio_size = len(tamil_audio)
                logger.info(f"✅ Successfully generated Tamil audio: {audio_size} bytes")
                
                # Save the audio to a file for verification
                filename = f"tamil_test_{name.lower().replace(' ', '_')}.mp3"
                with open(filename, "wb") as f:
                    f.write(tamil_audio)
                
                logger.info(f"✅ Tamil audio saved to {filename}")
                
                result = {
                    'name': name,
                    'text_length': len(text),
                    'audio_size': audio_size,
                    'quality': quality_info['quality'],
                    'size_kb': quality_info['size_kb'],
                    'duration_estimate': quality_info['duration_estimate'],
                    'filename': filename
                }
                results.append(result)
            else:
                logger.error(f"❌ Failed to generate Tamil audio for {name}")
                results.append({
                    'name': name,
                    'text_length': len(text),
                    'audio_size': 0,
                    'quality': 'failed',
                    'size_kb': 0,
                    'duration_estimate': 0,
                    'filename': None
                })
        
        # Print summary
        print("\n" + "="*70)
        print("ENHANCED TAMIL TTS QUALITY ASSESSMENT")
        print("="*70)
        print(f"{'Test Case':<20} {'Text Len':<10} {'Size (KB)':<10} {'Duration':<10} {'Quality':<15} {'File'}")
        print("-"*70)
        
        for result in results:
            print(f"{result['name']:<20} {result['text_length']:<10} {result['size_kb']:<10} {result['duration_estimate']:<10} {result['quality']:<15} {result['filename'] or 'N/A'}")
        
        print("="*70)
        
        # Calculate overall success rate
        successful = sum(1 for r in results if r['quality'] not in ['failed', 'very_poor', 'poor'])
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        print(f"\nOverall Success Rate: {success_rate:.1f}% ({successful}/{total} tests)")
        
        if success_rate >= 80:
            print("🎉 Tamil TTS is working excellently!")
        elif success_rate >= 60:
            print("✅ Tamil TTS is working well with good quality.")
        else:
            print("⚠️ Tamil TTS needs improvement.")
        
        return successful > 0
            
    except Exception as e:
        logger.error(f"Error in enhanced Tamil TTS test: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting enhanced Tamil TTS test...")
    
    success = test_enhanced_tamil_tts()
    
    if success:
        logger.info("🎉 Enhanced Tamil TTS test completed successfully!")
        return 0
    else:
        logger.error("❌ Enhanced Tamil TTS test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())