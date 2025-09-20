#!/usr/bin/env python3
"""
Diagnose audio generation issues in EchoVerse
"""

import sys
import os
from pathlib import Path
import tempfile

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def safe_count_voices(voices):
    """Safely count voices from pyttsx3"""
    voice_count = 0
    if voices:
        try:
            # Check if voices is a list or similar sequence
            if isinstance(voices, (list, tuple)):
                voice_count = len(voices)
            elif hasattr(voices, '__len__') and callable(getattr(voices, '__len__', None)):
                voice_count = voices.__len__()
            elif hasattr(voices, '__iter__') and callable(getattr(voices, '__iter__', None)):
                # Try to iterate and count
                count = 0
                try:
                    for _ in voices:
                        count += 1
                    voice_count = count
                except TypeError:
                    voice_count = 1
            else:
                voice_count = 1
        except Exception:
            voice_count = 1
    return voice_count

def diagnose_audio_issues():
    """Comprehensive diagnosis of audio generation issues"""
    print("🎙️ EchoVerse Audio Generation Diagnosis")
    print("=" * 50)
    
    # 1. Check if pyttsx3 is available
    print("\n1. Checking pyttsx3 availability...")
    try:
        import pyttsx3
        print("✅ pyttsx3 is available")
        
        # Try to initialize the engine
        try:
            engine = pyttsx3.init()
            print("✅ pyttsx3 engine initialized successfully")
            
            # Check available voices
            voices = engine.getProperty('voices')
            voice_count = safe_count_voices(voices)
            print(f"✅ Found {voice_count} available voices")
            
            # Try to speak a test phrase
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say("EchoVerse audio test")
            
            # Try to save to file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
                
            try:
                engine.save_to_file("EchoVerse audio test", temp_path)
                engine.runAndWait()
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    print("✅ Audio generation test successful")
                    os.unlink(temp_path)
                else:
                    print("❌ Audio generation test failed - no audio file created")
            except Exception as e:
                print(f"❌ Audio generation test failed: {e}")
                
        except Exception as e:
            print(f"❌ pyttsx3 engine initialization failed: {e}")
            
    except ImportError:
        print("❌ pyttsx3 is not installed")
        return False
    
    # 2. Check directory permissions
    print("\n2. Checking directory permissions...")
    project_root = Path(__file__).parent
    static_dir = project_root / "static"
    uploads_dir = static_dir / "uploads"
    output_dir = static_dir / "output"
    
    for dir_path in [project_root, static_dir, uploads_dir, output_dir]:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {dir_path}")
            except Exception as e:
                print(f"❌ Failed to create directory {dir_path}: {e}")
        else:
            print(f"✅ Directory exists: {dir_path}")
            
        # Check write permissions
        try:
            test_file = dir_path / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()
            print(f"✅ Write permissions OK for: {dir_path}")
        except Exception as e:
            print(f"❌ Write permissions issue for {dir_path}: {e}")
    
    # 3. Check app.py text_to_speech function
    print("\n3. Testing app.py text_to_speech function...")
    try:
        from app import text_to_speech
        
        # Create a test audio file
        test_text = "This is a test of the EchoVerse text to speech functionality."
        test_output = str(static_dir / "test_tts.wav")
        
        result = text_to_speech(
            text=test_text,
            output_path=test_output,
            voice_rate=175,
            voice_volume=0.9,
            voice_type='female_warm',
            target_language='en'
        )
        
        if os.path.exists(test_output) and os.path.getsize(test_output) > 0:
            print("✅ app.py text_to_speech function working correctly")
            print(f"   Generated file: {test_output}")
            os.unlink(test_output)  # Clean up
        else:
            print("❌ app.py text_to_speech function failed to generate audio")
            
    except Exception as e:
        print(f"❌ Error testing app.py text_to_speech function: {e}")
    
    # 4. Check IBM Watson TTS availability
    print("\n4. Checking IBM Watson TTS availability...")
    try:
        from services.voice_service import VoiceService
        
        # Try to initialize the service
        voice_service = VoiceService()
        print("✅ Voice service initialized successfully")
        
        # Check available voices
        voices = voice_service.get_available_voices()
        print(f"✅ Found {len(voices)} available voices in voice service")
        
        # Try to synthesize a short phrase
        test_text = "EchoVerse IBM Watson test"
        test_output = str(static_dir / "test_watson.wav")
        
        result = voice_service.synthesize_speech(test_text, test_output)
        if result and os.path.exists(test_output) and os.path.getsize(test_output) > 0:
            print("✅ Voice service TTS is available and working")
            print(f"   Generated file: {test_output}")
            os.unlink(test_output)  # Clean up
        else:
            print("❌ Voice service TTS failed to generate audio")
            
    except ImportError:
        print("ℹ️  Voice service not available (module not found)")
    except Exception as e:
        print(f"❌ Voice service error: {e}")
    
    # 5. Check system resources
    print("\n5. Checking system resources...")
    try:
        import psutil
        
        # Check available memory
        memory = psutil.virtual_memory()
        print(f"✅ Available memory: {memory.available / (1024**3):.2f} GB")
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"✅ CPU usage: {cpu_percent}%")
        
    except ImportError:
        print("ℹ️  psutil not available for system resource checking")
    except Exception as e:
        print(f"❌ System resource checking failed: {e}")
    
    print("\n" + "=" * 50)
    print("Diagnosis complete. Please review the results above.")
    return True

if __name__ == "__main__":
    diagnose_audio_issues()