#!/usr/bin/env python3
"""
Test script to simulate web interface audio generation
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def test_web_audio_generation():
    """Test the exact process used by the web interface"""
    print("🎙️ Testing Web Interface Audio Generation")
    print("=" * 50)
    
    try:
        # Import required functions from app.py
        from app import text_to_speech, extract_text_from_file
        import uuid
        from datetime import datetime
        
        # Create test content
        test_content = """
        This is a test of the EchoVerse audiobook generation system.
        The web interface should be able to convert this text to speech.
        If this test works, then the web interface should also work correctly.
        """
        
        # Create a test text file
        project_root = Path(__file__).parent
        static_dir = project_root / "static"
        uploads_dir = static_dir / "uploads"
        audio_dir = static_dir / "output"
        
        # Ensure directories exist
        uploads_dir.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test file
        test_file_path = uploads_dir / "test_web.txt"
        test_file_path.write_text(test_content, encoding='utf-8')
        print(f"✅ Created test file: {test_file_path}")
        
        # Extract text (simulating web interface)
        print("\n1. Extracting text from file...")
        text = extract_text_from_file(str(test_file_path))
        if not text:
            print("❌ Failed to extract text")
            return False
        print(f"✅ Extracted {len(text)} characters")
        
        # Generate audio filename (simulating web interface)
        audio_filename = f"audiobook_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_path = audio_dir / audio_filename
        print(f"2. Audio will be saved to: {audio_path}")
        
        # Call text_to_speech with the same parameters as the web interface
        print("\n3. Generating audio with web interface parameters...")
        success = text_to_speech(
            text=text,
            output_path=str(audio_path),
            voice_rate=175,
            voice_volume=0.9,
            voice_type='female_warm',
            target_language='en',
            enable_naturalness=True,
            continuous_flow=True,
            enable_ai_features=True
        )
        
        if success and audio_path.exists() and audio_path.stat().st_size > 0:
            print("✅ Audio generation successful!")
            print(f"   Generated file: {audio_path}")
            print(f"   File size: {audio_path.stat().st_size} bytes")
            return True
        else:
            print("❌ Audio generation failed")
            if audio_path.exists():
                print(f"   File exists but is empty: {audio_path.stat().st_size} bytes")
                # Clean up empty file
                audio_path.unlink()
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_web_audio_generation()
    if success:
        print("\n🎉 Web interface audio generation is working correctly!")
    else:
        print("\n💥 Web interface audio generation has issues!")