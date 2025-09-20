#!/usr/bin/env python3
"""
Debug script to identify why TTS service is failing in test_enhanced_tts.py
"""

import logging
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_tts():
    """Debug TTS issues"""
    print("=== Debugging TTS Service ===")
    
    # Import the service
    try:
        from services.enhanced_tts_service import EnhancedTTSService, TTSConfig, TTSProvider
        print("✅ EnhancedTTSService imported successfully")
    except Exception as e:
        print(f"❌ Failed to import EnhancedTTSService: {e}")
        return
    
    # Initialize service
    print("\n=== Service Initialization ===")
    try:
        tts_service = EnhancedTTSService()
        print("✅ EnhancedTTSService initialized")
        print(f"Available providers: {[p.value for p in tts_service.providers]}")
        print(f"Available languages: {len(tts_service.get_available_languages())}")
    except Exception as e:
        print(f"❌ Failed to initialize EnhancedTTSService: {e}")
        return
    
    # Test the exact same case as in test_enhanced_tts.py
    print("\n=== Testing Exact Case from test_enhanced_tts.py ===")
    lang_code = "en"
    text = "Hello, this is a test of the enhanced text-to-speech service."
    
    print(f"Testing language: {lang_code}")
    try:
        # Get available voices for this language
        voices = tts_service.get_voices_for_language(lang_code)
        print(f"  Available voices: {len(voices)}")
        if voices:
            for voice in voices:
                print(f"    - {voice.name} ({voice.provider.value})")
        
        # Check what provider would be selected
        selected_voice = tts_service.select_best_voice(lang_code)
        if selected_voice:
            print(f"  Selected voice: {selected_voice.name} ({selected_voice.provider.value})")
        else:
            print("  No voice selected")
        
        # Test each provider individually
        print("\n--- Testing Each Provider ---")
        
        # Test Edge TTS specifically
        print("\n  Testing Edge TTS:")
        config_edge = TTSConfig(
            text=text,
            language=lang_code,
            provider=TTSProvider.EDGE
        )
        audio_data_edge = tts_service.generate_speech(config_edge)
        if audio_data_edge:
            print(f"    ✅ Edge TTS Success: Generated {len(audio_data_edge)} bytes")
        else:
            print(f"    ❌ Edge TTS Failed")
        
        # Test gTTS specifically
        print("\n  Testing gTTS:")
        config_gtts = TTSConfig(
            text=text,
            language=lang_code,
            provider=TTSProvider.GTTS
        )
        audio_data_gtts = tts_service.generate_speech(config_gtts)
        if audio_data_gtts:
            print(f"    ✅ gTTS Success: Generated {len(audio_data_gtts)} bytes")
        else:
            print(f"    ❌ gTTS Failed")
            
        # Test pyttsx3 specifically
        print("\n  Testing pyttsx3:")
        config_pyttsx3 = TTSConfig(
            text=text,
            language=lang_code,
            provider=TTSProvider.PYTTSX3
        )
        audio_data_pyttsx3 = tts_service.generate_speech(config_pyttsx3)
        if audio_data_pyttsx3:
            print(f"    ✅ pyttsx3 Success: Generated {len(audio_data_pyttsx3)} bytes")
        else:
            print(f"    ❌ pyttsx3 Failed")
        
        # Generate speech with auto-selection
        config = TTSConfig(
            text=text,
            language=lang_code,
            speed=1.0
        )
        
        print(f"\n  TTSConfig: text={len(config.text)} chars, language={config.language}, provider={config.provider}")
        
        audio_data = tts_service.generate_speech(config)
        
        if audio_data:
            print(f"  ✅ Success: Generated {len(audio_data)} bytes of audio")
            
            # Save to file for verification
            filename = f"debug_test_{lang_code}.mp3"
            with open(filename, "wb") as f:
                f.write(audio_data)
            print(f"  📦 Audio saved to {filename}")
        else:
            print(f"  ❌ Failed: No audio generated")
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tts()