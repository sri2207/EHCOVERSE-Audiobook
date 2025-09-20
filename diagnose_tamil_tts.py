#!/usr/bin/env python3
"""
Diagnostic tool for Tamil TTS support and quality assessment
"""

import os
import sys
import logging
from typing import Dict, Any, List
import tempfile

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_tamil_tts_support() -> Dict[str, Any]:
    """Check Tamil TTS support and provide recommendations"""
    results = {
        'cloud_tts_available': False,
        'local_tts_available': False,
        'tamil_voice_support': False,
        'cloud_tts_quality': 'unknown',
        'local_tts_quality': 'unknown',
        'recommendations': []
    }
    
    gtts_module = None
    pyttsx3 = None
    
    try:
        # Check cloud TTS availability
        try:
            import importlib
            gtts_module = importlib.import_module('gtts')
            gTTS = getattr(gtts_module, 'gTTS')
            results['cloud_tts_available'] = True
            logger.info("✅ Google Cloud TTS (gTTS) is available")
        except Exception as e:
            results['cloud_tts_available'] = False
            logger.warning("⚠️ Google Cloud TTS (gTTS) is not available: %s", str(e))
            results['recommendations'].append("Install gTTS for better Tamil audio quality: pip install gTTS")
        
        # Check local TTS availability
        try:
            import pyttsx3 as pyttsx3_module
            pyttsx3 = pyttsx3_module
            engine = pyttsx3_module.init()
            voices = engine.getProperty('voices')
            if voices and isinstance(voices, (list, tuple)):
                results['local_tts_available'] = True
                logger.info("✅ Local TTS engine (pyttsx3) is available")
                
                # Check for Tamil voices
                tamil_voices = []
                for voice in voices:
                    voice_id = getattr(voice, 'id', str(voice))
                    voice_name = voice_id.lower()
                    if any(keyword in voice_name for keyword in ['tamil', 'ta', 'valluvar']):
                        tamil_voices.append(voice_id)
                
                if tamil_voices:
                    results['tamil_voice_support'] = True
                    logger.info("✅ Found Tamil-specific voices: %s", tamil_voices)
                else:
                    logger.warning("⚠️ No Tamil-specific voices found in local TTS engine")
                    results['recommendations'].append("Consider installing system Tamil voices for better local TTS quality")
            else:
                results['local_tts_available'] = False
                logger.warning("⚠️ Local TTS engine has no voices available or voices not in expected format")
                results['recommendations'].append("Local TTS engine has no voices - check system voice configuration")
                
        except Exception as e:
            results['local_tts_available'] = False
            logger.error("❌ Local TTS engine (pyttsx3) is not available: %s", str(e))
            results['recommendations'].append("Install pyttsx3 for local TTS fallback: pip install pyttsx3")
        
        # Test Tamil text generation
        test_tamil_text = "இது தமிழில் ஒரு சோதனை உரை. தமிழ் எழுத்துகளை சரியாக ஒலிபரப்ப உதவும்."
        logger.info("Testing Tamil text generation...")
        
        if results['cloud_tts_available'] and gtts_module:
            try:
                # Test cloud TTS with multiple voices
                gTTS = getattr(gtts_module, 'gTTS')
                best_quality = 0
                best_voice = None
                
                # Try different Tamil voices
                tamil_voices = ['ta', 'ta-in']
                for voice in tamil_voices:
                    try:
                        tts = gTTS(text=test_tamil_text, lang=voice, slow=True, lang_check=True)
                        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                            temp_path = temp_file.name
                        tts.save(temp_path)
                        file_size = os.path.getsize(temp_path)
                        os.unlink(temp_path)
                        
                        if file_size > best_quality:
                            best_quality = file_size
                            best_voice = voice
                            
                        logger.info("✅ Cloud TTS with voice '%s' generated Tamil audio: %d bytes", voice, file_size)
                    except Exception as e:
                        logger.warning("⚠️ Cloud TTS with voice '%s' failed: %s", voice, str(e))
                
                if best_quality > 0:
                    results['cloud_tts_quality'] = f'high ({best_quality} bytes with voice {best_voice})'
                    logger.info("✅ Cloud TTS generated Tamil audio successfully: %d bytes", best_quality)
                else:
                    results['cloud_tts_quality'] = 'low (no audio generated)'
                    logger.error("❌ Cloud TTS failed to generate meaningful Tamil audio")
                    results['recommendations'].append("Cloud TTS generated no meaningful audio - check internet connection and API access")
            except Exception as e:
                logger.error("❌ Cloud TTS failed for Tamil: %s", str(e))
                results['cloud_tts_quality'] = 'error'
                results['recommendations'].append("Cloud TTS failed for Tamil - check internet connection and API access")
        
        if results['local_tts_available'] and pyttsx3:
            try:
                # Test local TTS
                engine = pyttsx3.init()
                # Apply Tamil-specific settings
                engine.setProperty('rate', 140)
                engine.setProperty('volume', 1.0)
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                engine.save_to_file(test_tamil_text, temp_path)
                engine.runAndWait()
                file_size = os.path.getsize(temp_path)
                os.unlink(temp_path)
                
                # Assess quality based on file size
                if file_size > 10000:  # More than 10KB is considered good
                    results['local_tts_quality'] = f'good ({file_size} bytes)'
                elif file_size > 1000:  # More than 1KB is considered acceptable
                    results['local_tts_quality'] = f'acceptable ({file_size} bytes)'
                else:
                    results['local_tts_quality'] = f'poor ({file_size} bytes)'
                    
                logger.info("✅ Local TTS generated Tamil audio successfully: %d bytes (quality: %s)", file_size, results['local_tts_quality'])
            except Exception as e:
                logger.error("❌ Local TTS failed for Tamil: %s", str(e))
                results['local_tts_quality'] = 'error'
                results['recommendations'].append("Local TTS failed for Tamil - check system voice configuration")
        
    except Exception as e:
        logger.error("Error during Tamil TTS diagnostics: %s", str(e))
        results['recommendations'].append("Unexpected error during diagnostics: " + str(e))
    
    return results

def print_diagnostics_report(results: Dict[str, Any]) -> None:
    """Print a formatted diagnostics report"""
    print("\n" + "="*60)
    print("TAMIL TTS SUPPORT DIAGNOSTICS REPORT")
    print("="*60)
    
    print(f"\nCloud TTS Available: {'✅ YES' if results['cloud_tts_available'] else '❌ NO'}")
    print(f"Local TTS Available: {'✅ YES' if results['local_tts_available'] else '❌ NO'}")
    print(f"Tamil Voice Support: {'✅ YES' if results['tamil_voice_support'] else '⚠️ NO'}")
    
    if results['cloud_tts_available']:
        print(f"Cloud TTS Quality: {results['cloud_tts_quality']}")
    
    if results['local_tts_available']:
        print(f"Local TTS Quality: {results['local_tts_quality']}")
    
    if results['recommendations']:
        print("\nRECOMMENDATIONS:")
        for i, recommendation in enumerate(results['recommendations'], 1):
            print(f"  {i}. {recommendation}")
    else:
        print("\n✅ No issues detected. Tamil TTS should work well!")
    
    print("\nTIPS FOR BETTER TAMIL AUDIO QUALITY:")
    print("  1. Use cloud-based TTS (gTTS) for the best quality")
    print("  2. Install system Tamil voices for better local TTS")
    print("  3. Keep text properly formatted with punctuation")
    print("  4. Use shorter sentences for clearer pronunciation")
    print("  5. Consider using the EchoVerse web interface for best results")

def main():
    """Main diagnostic function"""
    logger.info("Starting Tamil TTS diagnostics...")
    results = check_tamil_tts_support()
    print_diagnostics_report(results)
    
    # Return appropriate exit code
    if results['cloud_tts_available'] or results['local_tts_available']:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())