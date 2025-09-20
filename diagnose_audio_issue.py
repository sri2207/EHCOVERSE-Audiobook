#!/usr/bin/env python3
"""
Diagnostic tool to identify audio generation issues in EchoVerse
"""

import os
import sys
import logging
import tempfile
import pyttsx3
from typing import Optional, Any, List, Union, cast

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pyttsx3_basic():
    """Test basic pyttsx3 functionality"""
    logger.info("=== Testing basic pyttsx3 functionality ===")
    
    try:
        # Initialize engine
        engine = pyttsx3.init()
        logger.info("✅ pyttsx3 engine initialized successfully")
        
        # Get available voices - cast to List for type checking
        voices_raw = engine.getProperty('voices')
        voices = cast(List[Any], voices_raw)
        logger.info(f"✅ Found {len(voices)} available voices:")
        for i, voice in enumerate(voices):
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = getattr(voice, 'name', 'Unknown')
            logger.info(f"  {i+1}. {voice_name} ({voice_id})")
        
        # Test basic speech generation
        test_text = "This is a test to verify that pyttsx3 is working correctly."
        logger.info("🎙️ Generating test speech...")
        
        # Try to generate speech to a temporary file
        temp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            engine.save_to_file(test_text, temp_path)
            engine.runAndWait()
            
            # Check if file was created and has content
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.info(f"✅ Audio file created successfully: {temp_path} ({file_size} bytes)")
                
                # Read the file content
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                logger.info(f"✅ Audio data read successfully: {len(audio_data)} bytes")
                
                # Clean up
                os.unlink(temp_path)
                logger.info("✅ Temporary file cleaned up")
                return True
            else:
                logger.error("❌ Audio file was not created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during speech generation: {e}")
            # Clean up temp file if it exists
            if temp_path is not None and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            return False
            
    except Exception as e:
        logger.error(f"❌ Error initializing pyttsx3: {e}")
        return False

def test_with_long_text():
    """Test pyttsx3 with longer text similar to what EchoVerse would process"""
    logger.info("=== Testing pyttsx3 with longer text ===")
    
    # Sample text similar to what EchoVerse processes
    long_text = """Once upon a time, in a quiet village nestled between rolling hills and whispering woods, there lived a young girl named Elena. She had always been curious about the world beyond her small home, dreaming of adventures that awaited in distant lands. Every evening, she would sit by her window and watch the stars, wondering what stories they might tell if only she could reach them.

One day, while exploring the forest near her village, Elena discovered an old, leather-bound book hidden beneath the roots of an ancient oak tree. As she opened the book, golden letters began to shimmer on the pages, and she realized this was no ordinary tome. It was a book of wishes, capable of bringing dreams to life.

With trembling hands, Elena wrote her deepest wish: to travel the world and help others find their own dreams. The moment she finished writing, the book glowed brightly, and a gentle wind lifted her off the ground. Her adventure was about to begin."""
    
    try:
        engine = pyttsx3.init()
        logger.info("✅ pyttsx3 engine initialized")
        
        # Configure engine properties
        engine.setProperty('rate', 175)  # words per minute
        engine.setProperty('volume', 0.8)
        
        logger.info("🎙️ Generating speech for longer text...")
        temp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            engine.save_to_file(long_text, temp_path)
            engine.runAndWait()
            
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.info(f"✅ Long text audio file created: {file_size} bytes")
                
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                logger.info(f"✅ Long text audio data: {len(audio_data)} bytes")
                
                os.unlink(temp_path)
                logger.info("✅ Temporary file cleaned up")
                return True
            else:
                logger.error("❌ Long text audio file was not created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during long text speech generation: {e}")
            if temp_path is not None and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            return False
            
    except Exception as e:
        logger.error(f"❌ Error with long text test: {e}")
        return False

def test_voice_selection():
    """Test voice selection functionality"""
    logger.info("=== Testing voice selection ===")
    
    try:
        engine = pyttsx3.init()
        voices_raw = engine.getProperty('voices')
        voices = cast(List[Any], voices_raw)
        logger.info(f"✅ Found {len(voices)} voices")
        
        if voices:
            # Try setting each voice and generating speech
            test_text = "Testing voice selection."
            for i, voice in enumerate(voices[:3]):  # Test first 3 voices
                temp_path: Optional[str] = None
                try:
                    voice_id = getattr(voice, 'id', str(voice))
                    logger.info(f"🎙️ Testing voice {i+1}: {voice_id}")
                    
                    engine.setProperty('voice', voice_id)
                    engine.setProperty('rate', 150)
                    engine.setProperty('volume', 0.7)
                    
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    engine.save_to_file(test_text, temp_path)
                    engine.runAndWait()
                    
                    if os.path.exists(temp_path):
                        file_size = os.path.getsize(temp_path)
                        logger.info(f"✅ Voice {i+1} working: {file_size} bytes")
                        # Clean up temp file
                        os.unlink(temp_path)
                        temp_path = None  # Reset after cleanup
                    else:
                        logger.warning(f"⚠️ Voice {i+1} generated no audio")
                        
                except Exception as e:
                    logger.error(f"❌ Error testing voice {i+1}: {e}")
                finally:
                    # Clean up temp file if it exists and wasn't already cleaned up
                    if temp_path is not None and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                        
        return True
    except Exception as e:
        logger.error(f"❌ Error in voice selection test: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    logger.info("Starting EchoVerse audio diagnostics...")
    
    # Test 1: Basic pyttsx3 functionality
    test1_result = test_pyttsx3_basic()
    
    # Test 2: Long text processing
    test2_result = test_with_long_text()
    
    # Test 3: Voice selection
    test3_result = test_voice_selection()
    
    # Summary
    logger.info("=== DIAGNOSTIC SUMMARY ===")
    logger.info(f"Basic pyttsx3 test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    logger.info(f"Long text test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    logger.info(f"Voice selection test: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    if all([test1_result, test2_result, test3_result]):
        logger.info("🎉 All tests passed! pyttsx3 is working correctly.")
        return True
    else:
        logger.error("❌ Some tests failed. There may be issues with pyttsx3 setup.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)