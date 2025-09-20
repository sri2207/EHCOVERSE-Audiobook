#!/usr/bin/env python3
"""
Test the TTS functionality directly
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def test_tts():
    """Test the text-to-speech functionality"""
    try:
        # Import the text-to-speech function from the existing codebase
        from app import text_to_speech
        
        # Test text
        test_text = """
        Welcome to EchoVerse, an advanced audiobook generation system. 
        This is a demonstration of the text-to-speech capabilities.
        The system can detect emotions in text and adjust the voice accordingly.
        For example, when it detects excitement, it speeds up the speech and increases volume.
        When it detects sadness, it slows down and softens the voice.
        This creates a more natural and engaging listening experience.
        """
        
        # Generate audiobook with different voices
        print("🎙️ Testing TTS functionality...")
        print("=" * 40)
        
        # Test 1: Female warm voice
        print("\n1. Testing Female Warm Voice...")
        success = text_to_speech(
            text=test_text,
            output_path="tts_test_female_warm.wav",
            voice_type="female_warm",
            enable_naturalness=True,
            continuous_flow=True
        )
        
        if success:
            print("✅ Female warm voice test successful")
            print(f"   File size: {Path('tts_test_female_warm.wav').stat().st_size / 1024:.0f} KB")
        else:
            print("❌ Female warm voice test failed")
        
        # Test 2: Male deep voice
        print("\n2. Testing Male Deep Voice...")
        success = text_to_speech(
            text=test_text,
            output_path="tts_test_male_deep.wav",
            voice_type="male_deep",
            enable_naturalness=True,
            continuous_flow=True
        )
        
        if success:
            print("✅ Male deep voice test successful")
            print(f"   File size: {Path('tts_test_male_deep.wav').stat().st_size / 1024:.0f} KB")
        else:
            print("❌ Male deep voice test failed")
        
        # Test 3: Cheerful energetic voice
        print("\n3. Testing Cheerful Energetic Voice...")
        success = text_to_speech(
            text="This is amazing! What an incredible demonstration of text-to-speech technology!",
            output_path="tts_test_cheerful.wav",
            voice_type="cheerful_energetic",
            enable_naturalness=True,
            continuous_flow=True
        )
        
        if success:
            print("✅ Cheerful energetic voice test successful")
            print(f"   File size: {Path('tts_test_cheerful.wav').stat().st_size / 1024:.0f} KB")
        else:
            print("❌ Cheerful energetic voice test failed")
            
        print("\n🎉 TTS testing completed!")
        print("\nTo play the generated audio files, you can:")
        print("1. Double-click on the WAV files in your file explorer")
        print("2. Use the command: python play_audiobooks.py tts_test_female_warm.wav")
        
    except Exception as e:
        print(f"❌ Error testing TTS functionality: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tts()