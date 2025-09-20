#!/usr/bin/env python3
"""
Test script for the Enhanced TTS Service
"""

import logging
import os
import sys

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.enhanced_tts_service import EnhancedTTSService, TTSConfig

def test_enhanced_tts():
    """Test the enhanced TTS service with multiple languages"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("Testing Enhanced TTS Service...")
    
    # Initialize the service
    tts_service = EnhancedTTSService()
    
    # Show available languages
    languages = tts_service.get_available_languages()
    print(f"Available languages: {len(languages)}")
    print(f"Sample languages: {sorted(languages)[:20]}")
    
    # Test different languages
    test_cases = [
        ("en", "Hello, this is a test of the enhanced text-to-speech service."),
        ("es", "Hola, esta es una prueba del servicio de texto a voz mejorado."),
        ("fr", "Bonjour, ceci est un test du service de synthèse vocale amélioré."),
        ("de", "Hallo, dies ist ein Test des verbesserten Sprachsyntheseservices."),
        ("it", "Ciao, questo è un test del servizio di sintesi vocale migliorato."),
        ("ja", "こんにちは、これは強化された音声合成サービスのテストです。"),
        ("ko", "안녕하세요, 이것은 향상된 텍스트 음성 변환 서비스 테스트입니다."),
        ("zh", "你好，这是增强文本转语音服务的测试。"),
        ("ru", "Привет, это тест улучшенной службы преобразования текста в речь."),
        ("ar", "مرحبا، هذا اختبار لخدمة تحويل النص إلى كلام المحسنة."),
        ("hi", "नमस्ते, यह उन्नत पाठ-से-भाषण सेवा का एक परीक्षण है।")
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for lang_code, text in test_cases:
        print(f"\nTesting language: {lang_code}")
        try:
            # Get available voices for this language
            voices = tts_service.get_voices_for_language(lang_code)
            print(f"  Available voices: {len(voices)}")
            if voices:
                print(f"  Sample voice: {voices[0].name} ({voices[0].provider.value})")
            
            # Generate speech
            config = TTSConfig(
                text=text,
                language=lang_code,
                speed=1.0
            )
            
            audio_data = tts_service.generate_speech(config)
            
            if audio_data:
                print(f"  ✅ Success: Generated {len(audio_data)} bytes of audio")
                successful_tests += 1
                
                # Save to file for verification
                filename = f"test_{lang_code}.mp3"
                with open(filename, "wb") as f:
                    f.write(audio_data)
                print(f"  📦 Audio saved to {filename}")
            else:
                print(f"  ❌ Failed: No audio generated")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Successful: {successful_tests}/{total_tests}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests > 0:
        print("\n🎉 Enhanced TTS Service is working correctly!")
        print("You can play the generated audio files to verify quality.")
    else:
        print("\n❌ Enhanced TTS Service failed all tests.")
        print("Please check your installation and dependencies.")

if __name__ == "__main__":
    test_enhanced_tts()