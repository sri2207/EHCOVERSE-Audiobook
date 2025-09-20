#!/usr/bin/env python3
"""
EchoVerse Audio Service
Handles audio generation with alternative TTS and fallback options
"""

import logging
import io
from typing import Optional, Dict, Any, Sized
import tempfile
import os

logger = logging.getLogger(__name__)

def safe_len(obj: Any) -> int:
    """Safely get the length of an object, returning 0 if it's None or not sized"""
    if obj is None:
        return 0
    if isinstance(obj, (str, list, tuple, dict, bytes)) or hasattr(obj, '__len__'):
        return len(obj)
    return 0

class EchoVerseAudioService:
    """Service for audio generation in EchoVerse"""
    
    def __init__(self):
        self.alternative_service = None
        self.tts_engine = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize audio service with alternative TTS and fallback"""
        try:
            from services.alternative_service import AlternativeService
            self.alternative_service = AlternativeService()
            logger.info("Alternative TTS service initialized")
        except ImportError as e:
            logger.warning(f"Alternative service not available, initializing fallback TTS: {e}")
            self._initialize_fallback_tts()
        except Exception as e:
            logger.warning(f"Alternative service initialization failed, using fallback TTS: {e}")
            self._initialize_fallback_tts()
    
    def _initialize_fallback_tts(self):
        """Initialize fallback TTS using pyttsx3"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            logger.info("Fallback TTS (pyttsx3) initialized")
        except ImportError:
            logger.error("No TTS engine available - install pyttsx3")
        except Exception as e:
            logger.error(f"Fallback TTS initialization failed: {e}")
    
    def generate_speech(self, text: str, voice: str = "Lisa", 
                       language: str = "en", audio_format: str = "mp3") -> Optional[bytes]:
        """Generate speech audio using alternative TTS or fallback"""
        logger.info(f"Audio service generating speech for {safe_len(text)} characters with voice={voice}, language={language}")
        
        # Try alternative TTS first
        if self.alternative_service:
            try:
                audio_data = self.alternative_service.generate_speech(
                    text=text,
                    voice=voice,
                    language=language,  # This was missing before!
                    audio_format=audio_format
                )
                if audio_data:
                    logger.info(f"Audio generated using alternative TTS with {voice} voice for language {language}")
                    return audio_data
                else:
                    logger.warning("Alternative TTS returned no audio data")
            except Exception as e:
                logger.error(f"Alternative TTS failed: {e}")
        
        # Fallback to local TTS
        logger.info(f"Using fallback TTS with {voice} voice for language {language}")
        return self._fallback_generate_speech(text, voice, language)
    
    def _fallback_generate_speech(self, text: str, voice: str, language: str) -> Optional[bytes]:
        """Generate speech using fallback TTS engine"""
        if not self.tts_engine:
            logger.error("No TTS engine available")
            return None
        
        # Import required modules at the beginning of the function
        import tempfile
        import os
        import time
        
        temp_path = None
        try:
            logger.info(f"Fallback generating speech for {safe_len(text)} characters with voice={voice}, language={language}")
            
            # Configure voice settings
            voices = self.tts_engine.getProperty('voices')
            voice_mapping = self._map_voice_to_system(voice, voices)
            
            if voice_mapping:
                self.tts_engine.setProperty('voice', voice_mapping)
                logger.info(f"Set fallback voice to: {voice_mapping}")
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 175)  # words per minute
            self.tts_engine.setProperty('volume', 0.8)
            
            # Generate audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                logger.info(f"Created fallback temporary file: {temp_path}")
            
            # Use the save_to_file method and runAndWait to generate the audio
            logger.info("Starting fallback audio generation...")
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()
            logger.info("Fallback audio generation completed")
            
            # Wait a moment to ensure file is written
            time.sleep(0.1)
            
            # Read the generated audio file
            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.info(f"Fallback temporary file size: {file_size} bytes")
                
                with open(temp_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                logger.info(f"Read {safe_len(audio_data)} bytes from fallback temporary file")
                
                # Clean up temporary file
                os.unlink(temp_path)
                logger.info("Fallback temporary file cleaned up")
                
                if audio_data and isinstance(audio_data, bytes) and safe_len(audio_data) > 0:
                    logger.info(f"Fallback audio generated: {safe_len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.error("Fallback audio data is empty")
                    return None
            else:
                logger.error("Fallback temporary file was not created")
                return None
            
        except Exception as e:
            logger.error(f"Fallback TTS generation failed: {e}")
            # Try to clean up temp file if it exists
            try:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info("Fallback temporary file cleaned up after error")
            except:
                pass
            return None
    
    def _map_voice_to_system(self, requested_voice: str, available_voices) -> Optional[str]:
        """Map requested voice to available system voices"""
        if not available_voices:
            return None
        
        # Voice preference mapping
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
        
        requested_prefs = voice_preferences.get(requested_voice, ["female"])
        
        # Find best matching voice
        for voice in available_voices:
            voice_id = voice.id if hasattr(voice, 'id') else str(voice)
            voice_name = voice_id.lower()
            
            # Check for exact matches first
            for pref in requested_prefs:
                if pref.lower() in voice_name:
                    logger.info(f"Mapped {requested_voice} to {voice_id}")
                    return voice_id
        
        # Default to first available voice
        default_voice = available_voices[0]
        default_id = default_voice.id if hasattr(default_voice, 'id') else str(default_voice)
        logger.info(f"Using default voice: {default_id}")
        return default_id
    
    def get_supported_voices(self) -> Dict[str, Any]:
        """Get supported voices information"""
        voices_info = {
            "premium_voices": [
                {
                    "id": "Lisa",
                    "name": "Lisa",
                    "description": "Female, warm and expressive",
                    "language": "en-US",
                    "sample_text": "Hello, I'm Lisa. I'll bring your stories to life with warmth and expression."
                },
                {
                    "id": "Michael", 
                    "name": "Michael",
                    "description": "Male, deep and authoritative",
                    "language": "en-US",
                    "sample_text": "Greetings, I'm Michael. I specialize in dramatic narration with depth and authority."
                },
                {
                    "id": "Allison",
                    "name": "Allison", 
                    "description": "Female, crisp and professional",
                    "language": "en-US",
                    "sample_text": "Hi there, I'm Allison. I deliver clear, professional narration perfect for any content."
                },
                {
                    "id": "Kevin",
                    "name": "Kevin",
                    "description": "Male, friendly and conversational", 
                    "language": "en-US",
                    "sample_text": "Hey, I'm Kevin! I bring a friendly, conversational style to every story."
                },
                {
                    "id": "Emma",
                    "name": "Emma",
                    "description": "Female, young and energetic",
                    "language": "en-US", 
                    "sample_text": "Hi! I'm Emma, and I love bringing energy and excitement to every narrative!"
                },
                {
                    "id": "Sophia",
                    "name": "Sophia",
                    "description": "Female, clear and articulate",
                    "language": "en-US",
                    "sample_text": "Hello, I'm Sophia. I provide clear and articulate narration perfect for educational content."
                },
                {
                    "id": "Olivia",
                    "name": "Olivia",
                    "description": "Female, soothing and calm",
                    "language": "en-US",
                    "sample_text": "Greetings, I'm Olivia. My soothing voice is perfect for meditation and relaxation content."
                },
                {
                    "id": "Ava",
                    "name": "Ava",
                    "description": "Female, vibrant and dynamic",
                    "language": "en-US",
                    "sample_text": "Hi there! I'm Ava, and I bring vibrant energy to every story I tell."
                }
            ]
        }
        
        return voices_info
    
    def get_audio_info(self, audio_data: bytes) -> Dict[str, Any]:
        """Get information about generated audio"""
        if not audio_data or not isinstance(audio_data, (bytes, bytearray)):
            return {}
        
        return {
            "size_bytes": safe_len(audio_data),
            "size_kb": round(safe_len(audio_data) / 1024, 2),
            "estimated_duration_seconds": safe_len(audio_data) / 16000,  # Rough estimate
            "format": "audio/wav or audio/mp3"
        }
    
    def validate_text_for_speech(self, text: str) -> Dict[str, Any]:
        """Validate text for speech generation"""
        issues = []
        recommendations = []
        
        if not text or not text.strip():
            issues.append("No text provided for speech generation")
            return {'valid': False, 'issues': issues, 'recommendations': recommendations}
        
        # Check text length
        char_count = safe_len(text)
        if char_count > 50000:  # Limit for single audio generation
            issues.append("Text is too long for single audio generation")
            recommendations.append("Consider breaking text into smaller chunks")
        elif char_count < 10:
            issues.append("Text is too short for meaningful audio")
            recommendations.append("Add more content for better audio generation")
        
        # Check for problematic characters
        problematic_chars = ['<', '>', '{', '}', '[', ']']
        found_problematic = [char for char in problematic_chars if char in text]
        if found_problematic:
            issues.append(f"Contains characters that may cause TTS issues: {', '.join(found_problematic)}")
            recommendations.append("Remove or replace special characters")
        
        # Estimate audio duration
        word_count = safe_len(text.split())
        estimated_duration = word_count / 150  # 150 words per minute average
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations,
            'estimated_duration_minutes': round(estimated_duration, 1),
            'word_count': word_count,
            'character_count': char_count
        }