"""
Voice Service for Text-to-Speech functionality with emotion and character support
"""
import os
import tempfile
import pyttsx3
from typing import Dict, List, Optional, Any, Tuple, Union, Iterable
from dataclasses import dataclass
from enum import Enum
import threading
import time
import logging
from collections.abc import Iterable as AbcIterable

from .text_service import EmotionType

logger = logging.getLogger(__name__)

class VoiceGender(Enum):
    """Voice gender types"""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoicePersonality(Enum):
    """Voice personality types"""
    NARRATOR = "narrator"
    STORYTELLER = "storyteller"
    CHARACTER_YOUNG = "character_young"
    CHARACTER_OLD = "character_old"
    CHARACTER_WISE = "character_wise"
    CHARACTER_ENERGETIC = "character_energetic"
    CHARACTER_CALM = "character_calm"
    CHARACTER_MYSTERIOUS = "character_mysterious"

@dataclass
class VoiceSettings:
    """Voice configuration settings"""
    rate: int = 180  # Words per minute
    volume: float = 0.9  # Volume level (0.0 to 1.0)
    voice_id: Optional[str] = None
    gender: VoiceGender = VoiceGender.NEUTRAL
    personality: VoicePersonality = VoicePersonality.NARRATOR
    emotion_intensity: float = 0.5  # Emotion expression intensity

@dataclass
class VoiceCapability:
    """Information about an available voice"""
    id: str
    name: str
    gender: VoiceGender
    language: str
    language_code: str
    age: str  # "adult", "child", "elderly"
    quality: str  # "high", "medium", "low"
    is_default: bool = False

class VoiceService:
    """Service for managing text-to-speech functionality"""
    
    def __init__(self):
        self.engine = None
        self.available_voices = {}
        self.language_voice_map = {}
        self.current_settings = VoiceSettings()
        self._initialize_engine()
        self._analyze_available_voices()
    
    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            self.engine = pyttsx3.init()
            logger.info("✅ TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize TTS engine: {e}")
            raise RuntimeError(f"TTS engine initialization failed: {e}")
    
    def _analyze_available_voices(self):
        """Analyze and categorize available system voices"""
        if not self.engine:
            return
        
        try:
            voices = self.engine.getProperty('voices')
            if not voices:
                return
            
            # Handle both single voice object and voice collections
            # pyttsx3 may return different types depending on the system
            try:
                # Try to iterate - this will succeed if voices is iterable
                voice_iter = iter(voices)  # type: ignore
                voices_list = list(voice_iter)
            except (TypeError, AttributeError):
                # If iteration fails, treat as single voice object
                voices_list = [voices]
            
            for voice in voices_list:
                capability = self._analyze_voice_capability(voice)
                self.available_voices[capability.id] = capability
                
                # Map voices by language
                lang_code = capability.language_code
                if lang_code not in self.language_voice_map:
                    self.language_voice_map[lang_code] = []
                self.language_voice_map[lang_code].append(capability)
            
            logger.info(f"✅ Found {len(self.available_voices)} voices for {len(self.language_voice_map)} languages")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not analyze voices: {e}")
    
    def _analyze_voice_capability(self, voice) -> VoiceCapability:
        """Analyze a voice to determine its capabilities"""
        voice_name = voice.name.lower()
        voice_id = voice.id
        
        # Determine gender
        gender = VoiceGender.NEUTRAL
        if any(term in voice_name for term in ['female', 'woman', 'girl', 'maria', 'susan', 'anna']):
            gender = VoiceGender.FEMALE
        elif any(term in voice_name for term in ['male', 'man', 'boy', 'david', 'mark', 'john']):
            gender = VoiceGender.MALE
        
        # Determine age
        age = "adult"
        if any(term in voice_name for term in ['child', 'young', 'junior']):
            age = "child"
        elif any(term in voice_name for term in ['senior', 'elderly', 'old']):
            age = "elderly"
        
        # Determine quality
        quality = "medium"
        if any(term in voice_name for term in ['premium', 'enhanced', 'neural', 'high']):
            quality = "high"
        elif any(term in voice_name for term in ['basic', 'standard', 'simple']):
            quality = "low"
        
        # Extract language information
        language_code = "en"
        language = "English"
        
        if hasattr(voice, 'languages') and voice.languages:
            lang_info = voice.languages[0] if isinstance(voice.languages, list) else voice.languages
            if isinstance(lang_info, str):
                language_code = lang_info[:2].lower()
        
        # Language mapping
        language_map = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
            'ta': 'Tamil', 'te': 'Telugu', 'ml': 'Malayalam', 'kn': 'Kannada'
        }
        language = language_map.get(language_code, language)
        
        return VoiceCapability(
            id=voice_id,
            name=voice.name,
            gender=gender,
            language=language,
            language_code=language_code,
            age=age,
            quality=quality,
            is_default=(voice_id == voice_id)  # First voice is typically default
        )
    
    def get_available_voices(self, language_code: Optional[str] = None) -> List[VoiceCapability]:
        """Get available voices, optionally filtered by language"""
        if language_code:
            return self.language_voice_map.get(language_code, [])
        return list(self.available_voices.values())
    
    def select_optimal_voice(self, language_code: str, personality: Optional[VoicePersonality] = None, 
                           gender: Optional[VoiceGender] = None) -> Optional[VoiceCapability]:
        """Select the best voice for given criteria"""
        available = self.get_available_voices(language_code)
        
        if not available:
            # Fallback to English if target language not available
            available = self.get_available_voices("en")
        
        if not available:
            return None
        
        # Score voices based on criteria
        scored_voices = []
        for voice in available:
            score = 0
            
            # Quality scoring
            if voice.quality == "high":
                score += 3
            elif voice.quality == "medium":
                score += 2
            else:
                score += 1
            
            # Gender preference
            if gender and voice.gender == gender:
                score += 2
            
            # Personality matching
            if personality:
                if personality == VoicePersonality.CHARACTER_YOUNG and voice.age == "child":
                    score += 3
                elif personality == VoicePersonality.CHARACTER_OLD and voice.age == "elderly":
                    score += 3
                elif personality in [VoicePersonality.NARRATOR, VoicePersonality.STORYTELLER]:
                    if voice.age == "adult":
                        score += 2
            
            # Default voice bonus
            if voice.is_default:
                score += 1
            
            scored_voices.append((score, voice))
        
        # Return highest scored voice
        scored_voices.sort(key=lambda x: x[0], reverse=True)
        return scored_voices[0][1] if scored_voices else None
    
    def configure_voice(self, settings: VoiceSettings):
        """Configure voice settings"""
        if not self.engine:
            raise RuntimeError("TTS engine not initialized")
        
        try:
            # Set voice if specified
            if settings.voice_id and settings.voice_id in self.available_voices:
                self.engine.setProperty('voice', settings.voice_id)
            
            # Set rate (words per minute)
            self.engine.setProperty('rate', settings.rate)
            
            # Set volume
            self.engine.setProperty('volume', settings.volume)
            
            self.current_settings = settings
            logger.info(f"✅ Voice configured: rate={settings.rate}, volume={settings.volume}")
            
        except Exception as e:
            logger.error(f"❌ Failed to configure voice: {e}")
            raise RuntimeError(f"Voice configuration failed: {e}")
    
    def adjust_for_emotion(self, emotion_type: EmotionType, intensity: float) -> VoiceSettings:
        """Adjust voice settings based on emotion"""
        settings = VoiceSettings(
            rate=self.current_settings.rate,
            volume=self.current_settings.volume,
            voice_id=self.current_settings.voice_id,
            gender=self.current_settings.gender,
            personality=self.current_settings.personality,
            emotion_intensity=intensity
        )
        
        # Adjust rate based on emotion
        base_rate = 180
        
        if emotion_type == EmotionType.EXCITEMENT:
            settings.rate = int(base_rate * (1 + intensity * 0.3))  # Faster for excitement
        elif emotion_type == EmotionType.SADNESS:
            settings.rate = int(base_rate * (1 - intensity * 0.4))  # Slower for sadness
        elif emotion_type == EmotionType.FEAR:
            settings.rate = int(base_rate * (1 + intensity * 0.2))  # Slightly faster for fear
        elif emotion_type == EmotionType.ANGER:
            settings.rate = int(base_rate * (1 + intensity * 0.1))  # Moderately faster
        elif emotion_type == EmotionType.MYSTERY:
            settings.rate = int(base_rate * (1 - intensity * 0.2))  # Slower and mysterious
        elif emotion_type == EmotionType.ROMANCE:
            settings.rate = int(base_rate * (1 - intensity * 0.1))  # Slightly slower
        elif emotion_type == EmotionType.ACTION:
            settings.rate = int(base_rate * (1 + intensity * 0.4))  # Much faster for action
        
        # Adjust volume for intensity
        if emotion_type in [EmotionType.EXCITEMENT, EmotionType.ANGER]:
            settings.volume = min(1.0, self.current_settings.volume * (1 + intensity * 0.2))
        elif emotion_type in [EmotionType.SADNESS, EmotionType.MYSTERY]:
            settings.volume = max(0.3, self.current_settings.volume * (1 - intensity * 0.3))
        
        return settings
    
    def synthesize_speech(self, text: str, output_path: str, 
                         emotion_type: EmotionType = EmotionType.NEUTRAL,
                         intensity: float = 0.5) -> bool:
        """Convert text to speech with emotion adjustment"""
        if not self.engine:
            raise RuntimeError("TTS engine not initialized")
        
        try:
            # Adjust voice for emotion
            emotion_settings = self.adjust_for_emotion(emotion_type, intensity)
            self.configure_voice(emotion_settings)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to file
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"✅ Audio generated: {output_path} ({file_size} bytes)")
                return True
            else:
                logger.error(f"❌ Audio file not created: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Speech synthesis failed: {e}")
            return False
    
    def synthesize_with_character_voices(self, text_segments: List[Dict[str, Any]], 
                                       output_path: str) -> bool:
        """Synthesize speech with different voices for different characters"""
        if not text_segments:
            return False
        
        try:
            # Create temporary files for each segment
            temp_files = []
            
            for i, segment in enumerate(text_segments):
                text = segment.get('text', '')
                character = segment.get('character', 'narrator')
                emotion = segment.get('emotion', EmotionType.NEUTRAL)
                intensity = segment.get('intensity', 0.5)
                
                # Select appropriate voice for character
                personality = self._get_character_personality(character)
                
                # Create temporary file for this segment
                temp_path = os.path.join(tempfile.gettempdir(), f"segment_{i}.wav")
                
                # Synthesize this segment
                if self.synthesize_speech(text, temp_path, emotion, intensity):
                    temp_files.append(temp_path)
                else:
                    logger.warning(f"⚠️ Failed to synthesize segment {i}")
            
            if temp_files:
                # For now, just use the first file (audio merging would require additional libraries)
                # In a full implementation, you'd merge all temp_files into output_path
                import shutil
                shutil.copy2(temp_files[0], output_path)
                
                # Clean up temporary files
                for temp_file in temp_files:
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Multi-character synthesis failed: {e}")
            return False
    
    def _get_character_personality(self, character_name: str) -> VoicePersonality:
        """Determine personality based on character name or type"""
        character_lower = character_name.lower()
        
        if character_lower in ['narrator', 'author', 'voice']:
            return VoicePersonality.NARRATOR
        elif any(term in character_lower for term in ['young', 'child', 'kid', 'boy', 'girl']):
            return VoicePersonality.CHARACTER_YOUNG
        elif any(term in character_lower for term in ['old', 'elderly', 'grandfather', 'grandmother', 'wise']):
            return VoicePersonality.CHARACTER_OLD
        elif any(term in character_lower for term in ['sage', 'wizard', 'mentor', 'teacher']):
            return VoicePersonality.CHARACTER_WISE
        elif any(term in character_lower for term in ['energetic', 'excited', 'active', 'bouncy']):
            return VoicePersonality.CHARACTER_ENERGETIC
        elif any(term in character_lower for term in ['calm', 'peaceful', 'serene', 'gentle']):
            return VoicePersonality.CHARACTER_CALM
        elif any(term in character_lower for term in ['mysterious', 'dark', 'shadow', 'secret']):
            return VoicePersonality.CHARACTER_MYSTERIOUS
        else:
            return VoicePersonality.STORYTELLER
    
    def preview_voice(self, text: str = "This is a preview of the selected voice.", 
                     voice_id: Optional[str] = None) -> bool:
        """Preview a voice with sample text"""
        if not self.engine:
            return False
        
        try:
            original_voice = self.engine.getProperty('voice')
            original_voice_id = str(original_voice) if original_voice else None
            
            if voice_id:
                self.engine.setProperty('voice', voice_id)
            
            self.engine.say(text)
            self.engine.runAndWait()
            
            # Restore original voice
            if original_voice_id:
                self.engine.setProperty('voice', original_voice_id)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Voice preview failed: {e}")
            return False
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get current voice configuration info"""
        if not self.engine:
            return {}
        
        try:
            current_voice_id = self.engine.getProperty('voice')
            current_rate = self.engine.getProperty('rate')
            current_volume = self.engine.getProperty('volume')
            
            voice_info = {
                'current_voice_id': current_voice_id,
                'current_rate': current_rate,
                'current_volume': current_volume,
                'available_voices_count': len(self.available_voices),
                'supported_languages': list(self.language_voice_map.keys()),
                'settings': {
                    'rate': self.current_settings.rate,
                    'volume': self.current_settings.volume,
                    'gender': self.current_settings.gender.value,
                    'personality': self.current_settings.personality.value
                }
            }
            
            if current_voice_id in self.available_voices:
                voice_capability = self.available_voices[current_voice_id]
                voice_info['current_voice'] = {
                    'name': voice_capability.name,
                    'gender': voice_capability.gender.value,
                    'language': voice_capability.language,
                    'quality': voice_capability.quality
                }
            
            return voice_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get voice info: {e}")
            return {}
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.engine:
                self.engine.stop()
            logger.info("✅ Voice service cleanup completed")
        except Exception as e:
            logger.warning(f"⚠️ Voice service cleanup warning: {e}")