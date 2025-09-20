import os
import sys
from deep_translator import GoogleTranslator
import langdetect

def test_translation():
    """Test the translation functionality"""
    print("Testing translation functionality...")
    
    # Test text in English
    text = "Hello, how are you today? This is a test of the translation system."
    print(f"Original text: {text}")
    
    # Detect language
    try:
        detected_lang = langdetect.detect(text)
        print(f"Detected language: {detected_lang}")
    except Exception as e:
        print(f"Language detection failed: {e}")
        detected_lang = 'en'
    
    # Test translation to Spanish
    try:
        translator = GoogleTranslator(source='en', target='es')
        translated = translator.translate(text)
        print(f"Translated to Spanish: {translated}")
        print("✅ Translation test PASSED")
        return True
    except Exception as e:
        print(f"❌ Translation test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_translation()