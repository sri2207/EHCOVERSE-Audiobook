#!/usr/bin/env python3
"""
Test audio playback directly using Python
"""

import sys
import os
from pathlib import Path

def play_audio_with_system(filepath):
    """Play audio file using system default player"""
    try:
        if sys.platform == "win32":
            os.system(f'start /min "" "{filepath}"')
        elif sys.platform == "darwin":
            os.system(f'afplay "{filepath}"')
        else:
            os.system(f'aplay "{filepath}" &')
        return True
    except Exception as e:
        print(f"Error playing with system player: {e}")
        return False

def test_audio_files():
    """Test playing the generated audio files"""
    print("🔊 Testing Audio Playback")
    print("=" * 30)
    
    # List of generated audio files
    audio_files = [
        "tts_test_female_warm.wav",
        "tts_test_male_deep.wav", 
        "tts_test_cheerful.wav"
    ]
    
    for i, filename in enumerate(audio_files, 1):
        if os.path.exists(filename):
            file_size = Path(filename).stat().st_size / 1024
            print(f"\n{i}. {filename} ({file_size:.0f} KB)")
            
            # Play with system player
            print("   Playing with system player...")
            if play_audio_with_system(filename):
                print("   ✅ Played successfully with system player")
            else:
                print("   ❌ Failed to play")
        else:
            print(f"\n{i}. {filename} - File not found")
    
    print("\n🎵 Audio playback test completed!")
    print("\nIf you didn't hear anything, try:")
    print("1. Checking your system volume settings")
    print("2. Verifying your default audio player works")
    print("3. Opening the WAV files directly in your file explorer")

if __name__ == "__main__":
    test_audio_files()