#!/usr/bin/env python3
"""
Example usage of the Enhanced TTS Service
"""

import logging
import os
import sys

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.enhanced_tts_service import EnhancedTTSService, TTSConfig

def main():
    """Demonstrate the enhanced TTS service capabilities"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the enhanced TTS service
    tts_service = EnhancedTTSService()
    
    print("=== Enhanced TTS Service Demo ===")
    print(f"Supported languages: {len(tts_service.get_available_languages())}")
    
    # Example 1: Simple English speech generation
    print("\n1. Generating English speech...")
    config = TTSConfig(
        text="Welcome to the enhanced text-to-speech service. This demonstration shows how to generate high-quality audio in multiple languages.",
        language="en"
    )
    audio_data = tts_service.generate_speech(config)
    if audio_data:
        with open("demo_english.mp3", "wb") as f:
            f.write(audio_data)
        print("✅ English audio saved as demo_english.mp3")
    
    # Example 2: Spanish with speed control
    print("\n2. Generating Spanish speech with fast speed...")
    config = TTSConfig(
        text="¡Hola! Esta es una demostración de texto a voz en español con velocidad rápida.",
        language="es",
        speed=1.3  # 30% faster
    )
    audio_data = tts_service.generate_speech(config)
    if audio_data:
        with open("demo_spanish_fast.mp3", "wb") as f:
            f.write(audio_data)
        print("✅ Fast Spanish audio saved as demo_spanish_fast.mp3")
    
    # Example 3: Japanese with specific provider
    print("\n3. Generating Japanese speech...")
    config = TTSConfig(
        text="こんにちは。これは日本語の音声合成のデモンストレーションです。",
        language="ja"
    )
    audio_data = tts_service.generate_speech(config)
    if audio_data:
        with open("demo_japanese.mp3", "wb") as f:
            f.write(audio_data)
        print("✅ Japanese audio saved as demo_japanese.mp3")
    
    # Example 4: Show available voices for a specific language
    print("\n4. Available voices for French:")
    french_voices = tts_service.get_voices_for_language("fr")
    for voice in french_voices:
        print(f"   - {voice.name} (Provider: {voice.provider.value}, Quality: {voice.quality})")
    
    # Example 5: Select best voice for a language
    print("\n5. Best voice for German:")
    best_voice = tts_service.select_best_voice("de")
    if best_voice:
        print(f"   - {best_voice.name} (Provider: {best_voice.provider.value})")
    
    print("\n🎉 Demo completed! Check the generated MP3 files.")

if __name__ == "__main__":
    main()