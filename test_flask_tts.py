#!/usr/bin/env python3
"""
Test Flask TTS endpoint directly
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def test_flask_tts():
    """Test the Flask TTS functionality"""
    try:
        # Import the text-to-speech function from the existing codebase
        from app import text_to_speech, extract_text_from_file
        
        print("🎙️ Testing Flask TTS Functionality")
        print("=" * 40)
        
        # Test with a sample document
        sample_file = "sample_docs/sample_text.txt"
        
        if not Path(sample_file).exists():
            print(f"❌ Sample file {sample_file} not found")
            return
            
        print(f"📄 Reading text from {sample_file}...")
        text = extract_text_from_file(sample_file)
        
        if not text:
            print("❌ Failed to extract text from file")
            return
            
        print(f"✅ Extracted {len(text)} characters")
        
        # Test TTS with Flask endpoint settings
        print("\n🔊 Generating audiobook with Flask settings...")
        success = text_to_speech(
            text=text,
            output_path="flask_test_output.wav",
            voice_rate=175,
            voice_volume=0.9,
            voice_type="female_warm",
            enable_naturalness=True,
            continuous_flow=True,
            enable_ai_features=True
        )
        
        if success:
            file_size = Path("flask_test_output.wav").stat().st_size / 1024
            print(f"✅ Flask TTS test successful ({file_size:.0f} KB)")
        else:
            print("❌ Flask TTS test failed")
            
    except Exception as e:
        print(f"❌ Error testing Flask TTS functionality: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flask_tts()