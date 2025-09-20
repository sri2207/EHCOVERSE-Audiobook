#!/usr/bin/env python3
"""
Fix for audio generation issues in EchoVerse
"""

import os
import sys
import logging
import tempfile
import pyttsx3
from typing import Optional

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioGenerationFix:
    """Fix for audio generation issues"""
    
    def __init__(self):
        self.tts_engine = None
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize TTS engine with better error handling"""
        try:
            self.tts_engine = pyttsx3.init()
            logger.info("✅ TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize TTS engine: {e}")
            self.tts_engine = None
    
    def generate_audio_with_retry(self, text: str, voice: str = "Lisa", 
                                 language: str = "en", max_retries: int = 3) -> Optional[bytes]:
        """Generate audio with retry mechanism and better error handling"""
        if not self.tts_engine:
            logger.error("❌ TTS engine not available")
            return None
        
        if not text or not text.strip():
            logger.error("❌ No text provided for audio generation")
            return None
        
        logger.info(f"Generating audio for {len(text)} characters with voice={voice}, language={language}")
        
        # Try multiple times
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_retries}")
                
                # Configure engine
                self.tts_engine.setProperty('rate', 175)
                self.tts_engine.setProperty('volume', 0.8)
                
                # Set voice based on language
                voices = self.tts_engine.getProperty('voices')
                voice_id = self._map_voice_for_language(voice, voices, language)
                
                if voice_id:
                    self.tts_engine.setProperty('voice', voice_id)
                    logger.info(f"Set voice to: {voice_id}")
                
                # Generate to temporary file with better handling
                temp_path = None
                try:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_path = temp_file.name
                        logger.info(f"Created temporary file: {temp_path}")
                    
                    # Generate audio
                    logger.info("Starting audio generation...")
                    self.tts_engine.save_to_file(text, temp_path)
                    self.tts_engine.runAndWait()
                    logger.info("Audio generation completed")
                    
                    # Check file
                    if os.path.exists(temp_path):
                        file_size = os.path.getsize(temp_path)
                        logger.info(f"Generated file size: {file_size} bytes")
                        
                        if file_size > 0:
                            # Read audio data
                            with open(temp_path, 'rb') as f:
                                audio_data = f.read()
                            
                            logger.info(f"Successfully read {len(audio_data)} bytes")
                            
                            # Clean up
                            os.unlink(temp_path)
                            logger.info("Temporary file cleaned up")
                            
                            return audio_data
                        else:
                            logger.error("Generated file is empty")
                    else:
                        logger.error("Temporary file was not created")
                
                except Exception as e:
                    logger.error(f"Error during audio generation: {e}")
                    # Clean up temp file if it exists
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                            logger.info("Temporary file cleaned up after error")
                        except Exception as cleanup_error:
                            logger.error(f"Failed to clean up temporary file: {cleanup_error}")
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info("Retrying...")
                    continue
                else:
                    logger.error("All attempts failed")
                    return None
        
        return None
    
    def _map_voice_for_language(self, requested_voice: str, available_voices, language: str) -> Optional[str]:
        """Map voice considering language"""
        if not available_voices:
            return None
        
        logger.info(f"Mapping voice '{requested_voice}' for language '{language}'")
        
        # Voice preferences
        voice_preferences = {
            "Lisa": ["microsoft zira", "female", "woman"],
            "Michael": ["microsoft david", "male", "man"],
            "Allison": ["microsoft hazel", "female", "woman"],
            "Kevin": ["microsoft mark", "male", "man"],
            "Emma": ["microsoft eva", "female", "woman"],
            "Sophia": ["microsoft zira", "female", "woman"],
            "Olivia": ["microsoft zira", "female", "woman"],
            "Ava": ["microsoft zira", "female", "woman"]
        }
        
        # Language preferences
        language_prefs = {
            "es": ["spanish", "es"],
            "fr": ["french", "fr"],
            "de": ["german", "de"],
            "it": ["italian", "it"],
            "pt": ["portuguese", "pt"],
            "hi": ["hindi", "hi"],
            "zh": ["chinese", "zh"],
            "ja": ["japanese", "ja"],
            "ta": ["tamil", "ta"],
            "en": ["english", "en", "microsoft"]
        }
        
        requested_prefs = voice_preferences.get(requested_voice, ["female"])
        lang_prefs = language_prefs.get(language, [language])
        
        # Look for best match
        for voice in available_voices:
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = voice_id.lower()
            
            # Check language match first
            language_match = any(pref in voice_name for pref in lang_prefs)
            if language_match:
                # Then check voice match
                voice_match = any(pref.lower() in voice_name for pref in requested_prefs)
                if voice_match:
                    logger.info(f"Perfect match found: {voice_id}")
                    return voice_id
        
        # Language-only match
        for voice in available_voices:
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = voice_id.lower()
            
            language_match = any(pref in voice_name for pref in lang_prefs)
            if language_match:
                logger.info(f"Language match found: {voice_id}")
                return voice_id
        
        # Default to first available voice
        if available_voices:
            default_voice = available_voices[0]
            default_id = getattr(default_voice, 'id', str(default_voice))
            logger.info(f"Using default voice: {default_id}")
            return default_id
        
        return None

def test_fix():
    """Test the audio generation fix"""
    logger.info("=== Testing audio generation fix ===")
    
    fix = AudioGenerationFix()
    
    if not fix.tts_engine:
        logger.error("❌ Failed to initialize fix")
        return False
    
    # Test cases
    test_cases = [
        ("English test", "Lisa", "en"),
        ("Prueba en español", "Lisa", "es"),
        ("தமிழ் சோதனை", "Lisa", "ta"),  # Tamil
    ]
    
    success_count = 0
    
    for text, voice, language in test_cases:
        logger.info(f"Testing: '{text[:20]}...' with voice={voice}, language={language}")
        
        audio_data = fix.generate_audio_with_retry(text, voice, language)
        
        if audio_data and len(audio_data) > 0:
            logger.info(f"✅ Success: Generated {len(audio_data)} bytes")
            success_count += 1
        else:
            logger.error("❌ Failed to generate audio")
    
    logger.info(f"=== Results: {success_count}/{len(test_cases)} successful ===")
    
    return success_count == len(test_cases)

def main():
    """Main function"""
    logger.info("Starting audio generation fix test...")
    
    result = test_fix()
    
    if result:
        logger.info("🎉 All tests passed! Audio generation fix is working.")
        return True
    else:
        logger.error("❌ Some tests failed. Audio generation issues remain.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)