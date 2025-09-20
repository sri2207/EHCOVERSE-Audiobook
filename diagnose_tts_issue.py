#!/usr/bin/env python3
"""
Diagnostic script to identify TTS issues
"""

import logging
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_tts():
    """Diagnose TTS issues"""
    print("=== TTS Diagnostic ===")
    
    # Import the service
    try:
        from services.enhanced_tts_service import EnhancedTTSService, TTSConfig, TTSProvider
        print("✅ EnhancedTTSService imported successfully")
    except Exception as e:
        print(f"❌ Failed to import EnhancedTTSService: {e}")
        return
    
    # Check available providers
    print("\n=== Provider Status ===")
    try:
        from services.enhanced_tts_service import GTTS_AVAILABLE, POLLY_AVAILABLE, EDGE_AVAILABLE, PYTTSX3_AVAILABLE, COQUI_AVAILABLE
        print(f"GTTS_AVAILABLE: {GTTS_AVAILABLE}")
        print(f"POLLY_AVAILABLE: {POLLY_AVAILABLE}")
        print(f"EDGE_AVAILABLE: {EDGE_AVAILABLE}")
        print(f"PYTTSX3_AVAILABLE: {PYTTSX3_AVAILABLE}")
        print(f"COQUI_AVAILABLE: {COQUI_AVAILABLE}")
    except Exception as e:
        print(f"❌ Failed to check provider status: {e}")
    
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
    
    # Test each provider individually
    print("\n=== Individual Provider Tests ===")
    
    # Test gTTS
    print("\n--- Testing gTTS ---")
    try:
        config = TTSConfig(
            text="This is a test of gTTS.",
            language="en",
            provider=TTSProvider.GTTS
        )
        audio_data = tts_service.generate_speech(config)
        if audio_data:
            print(f"✅ gTTS generated audio: {len(audio_data)} bytes")
        else:
            print("❌ gTTS failed to generate audio")
    except Exception as e:
        print(f"❌ gTTS test failed: {e}")
    
    # Test pyttsx3
    print("\n--- Testing pyttsx3 ---")
    try:
        config = TTSConfig(
            text="This is a test of pyttsx3.",
            language="en",
            provider=TTSProvider.PYTTSX3
        )
        audio_data = tts_service.generate_speech(config)
        if audio_data:
            print(f"✅ pyttsx3 generated audio: {len(audio_data)} bytes")
        else:
            print("❌ pyttsx3 failed to generate audio")
    except Exception as e:
        print(f"❌ pyttsx3 test failed: {e}")
    
    # Test Polly
    print("\n--- Testing Polly ---")
    try:
        config = TTSConfig(
            text="This is a test of Polly.",
            language="en",
            provider=TTSProvider.POLLY
        )
        audio_data = tts_service.generate_speech(config)
        if audio_data:
            print(f"✅ Polly generated audio: {len(audio_data)} bytes")
        else:
            print("❌ Polly failed to generate audio (may be due to missing AWS credentials)")
    except Exception as e:
        print(f"❌ Polly test failed: {e}")

if __name__ == "__main__":
    diagnose_tts()