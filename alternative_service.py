"""
Alternative Service Implementation for EchoVerse
Replaces IBM Watson services with alternative solutions using your API key
"""

import os
import logging
import requests
import json
from typing import Optional, Dict, Any, Union
import pyttsx3
import io
import tempfile

# Add safe_len function to handle type checking issues
def safe_len(obj: Any) -> int:
    """Safely get the length of an object, returning 0 if it's None or not sized"""
    if obj is None:
        return 0
    if isinstance(obj, (str, list, tuple, dict, bytes)) or hasattr(obj, '__len__'):
        return len(obj)
    return 0

# Try to import gTTS for cloud-based TTS
GttsAvailable = False
gTTS = None

# Use try-except with a broader exception to handle import errors
try:
    # We're using a string-based import to avoid static analysis issues
    import importlib
    gtts_module = importlib.import_module('gtts')
    gTTS = getattr(gtts_module, 'gTTS')
    GttsAvailable = True
    logging.info("✅ gTTS library available for cloud-based TTS")
except Exception:
    logging.info("ℹ️ gTTS library not available, will use local TTS only")

# Try to import our enhanced TTS service
EnhancedTtsAvailable = False
EnhancedTTSService = None
TTSConfig = None

try:
    from services.enhanced_tts_service import EnhancedTTSService as EnhancedTTSServiceImport, TTSConfig as TTSConfigImport
    EnhancedTTSService = EnhancedTTSServiceImport
    TTSConfig = TTSConfigImport
    EnhancedTtsAvailable = True
    logging.info("✅ Enhanced TTS service available")
except ImportError:
    logging.info("ℹ️ Enhanced TTS service not available, using basic TTS only")
except Exception as e:
    logging.warning(f"⚠️ Enhanced TTS service initialization error: {e}")

logger = logging.getLogger(__name__)

class AlternativeService:
    """Alternative service implementation using various APIs and fallbacks"""
    
    def __init__(self):
        # Use your API key
        self.api_key = os.getenv('AUDIOBOOK_API_KEY', 'ap2_c51760e0-4886-4ca9-80e6-287eeb352592')
        self._initialize_services()
        # Enhanced TTS service for better language support
        self.enhanced_tts = EnhancedTTSService() if EnhancedTtsAvailable and EnhancedTTSService else None
        # Language support tracking - extended to 100+ languages
        self.supported_languages = {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
            "nl": "Dutch",
            "sv": "Swedish",
            "pl": "Polish",
            "tr": "Turkish",
            "cs": "Czech",
            "el": "Greek",
            "he": "Hebrew",
            "th": "Thai",
            "vi": "Vietnamese",
            "id": "Indonesian",
            "ms": "Malay",
            "fil": "Filipino",
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "ml": "Malayalam",
            "kn": "Kannada",
            "mr": "Marathi",
            "gu": "Gujarati",
            "pa": "Punjabi",
            "ur": "Urdu",
            "fa": "Persian",
            "ro": "Romanian",
            "hu": "Hungarian",
            "uk": "Ukrainian",
            "bg": "Bulgarian",
            "hr": "Croatian",
            "sk": "Slovak",
            "sl": "Slovenian",
            "sr": "Serbian",
            "lt": "Lithuanian",
            "lv": "Latvian",
            "et": "Estonian",
            "mt": "Maltese",
            "sq": "Albanian",
            "mk": "Macedonian",
            "bs": "Bosnian",
            "is": "Icelandic",
            "ga": "Irish",
            "cy": "Welsh",
            "eu": "Basque",
            "ca": "Catalan",
            "gl": "Galician",
            "af": "Afrikaans",
            "sw": "Swahili",
            "zu": "Zulu",
            "xh": "Xhosa"
        }
        # Additional languages that require special handling
        self.extended_languages = {
            "yue": "Cantonese",
            "zh-TW": "Traditional Chinese",
            "jv": "Javanese",
            "su": "Sundanese",
            "my": "Burmese",
            "km": "Khmer",
            "lo": "Lao",
            "si": "Sinhala",
            "am": "Amharic",
            "om": "Oromo",
            "so": "Somali",
            "ti": "Tigrinya",
            "ha": "Hausa",
            "yo": "Yoruba",
            "ig": "Igbo",
            "sn": "Shona",
            "st": "Sesotho",
            "tn": "Setswana",
            "ts": "Tsonga",
            "ve": "Venda",
            "nr": "Ndebele",
            "ss": "Swazi",
            "ki": "Kikuyu",
            "lu": "Luba-Katanga",
            "ny": "Chichewa",
            "rw": "Kinyarwanda",
            "rn": "Kirundi",
            "mg": "Malagasy",
            "eo": "Esperanto"
        }
    
    def _initialize_services(self):
        """Initialize alternative services"""
        try:
            # Initialize Google Translator as replacement for IBM Language Translator
            from deep_translator import GoogleTranslator
            self.translator_service = GoogleTranslator(source='auto', target='en')
            logger.info("✅ Google Translator service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Google Translator initialization failed: {e}")
            self.translator_service = None
        
        # Initialize pyttsx3 for local TTS as fallback
        try:
            self.tts_engine = pyttsx3.init()
            logger.info("✅ Local TTS engine (pyttsx3) initialized")
        except Exception as e:
            logger.warning(f"⚠️ Local TTS engine initialization failed: {e}")
            self.tts_engine = None
    
    def generate_speech(self, text: str, voice: str = "Lisa", 
                        language: str = "en", audio_format: str = "audio/mp3") -> Optional[bytes]:
        """Generate speech audio using alternative methods with enhanced language support"""
        try:
            logger.info(f"Generating speech for {safe_len(text)} characters with voice={voice}, language={language}")
            
            # Try enhanced TTS first for better language support
            if self.enhanced_tts and language in self.supported_languages:
                logger.info(f"Using enhanced TTS for language: {language}")
                if TTSConfig:
                    config = TTSConfig(
                        text=text,
                        language=language,
                        audio_format=audio_format.replace("audio/", "")
                    )
                    result = self.enhanced_tts.generate_speech(config)
                    if result:
                        logger.info(f"Successfully generated audio using enhanced TTS: {safe_len(result)} bytes")
                        return result
                    else:
                        logger.warning("Enhanced TTS failed, falling back to traditional methods")
            
            # For Tamil language, try to use cloud-based TTS for better quality
            if language == "ta":
                if GttsAvailable:
                    logger.info("Using cloud-based TTS for Tamil language for better quality")
                    cloud_tts_result = self._generate_cloud_tts(text, voice, language, audio_format)
                    if cloud_tts_result:
                        logger.info(f"Successfully generated audio using cloud TTS: {safe_len(cloud_tts_result)} bytes")
                        return cloud_tts_result
                    else:
                        logger.warning("Cloud TTS failed for Tamil, falling back to local TTS")
                else:
                    logger.info("gTTS not available, using enhanced local TTS for Tamil")
                    # Apply enhanced preprocessing for Tamil when cloud TTS is not available
                    enhanced_text = self._preprocess_tamil_for_local_tts(text)
                    local_result = self._generate_local_speech(enhanced_text, voice, language)
                    if local_result and safe_len(local_result) > 50:  # Ensure reasonable audio size
                        logger.info(f"Successfully generated enhanced local Tamil audio: {safe_len(local_result)} bytes")
                        return local_result
                    else:
                        logger.warning("Enhanced local TTS failed for Tamil, trying basic local TTS")
            
            # Try to use local TTS engine
            if self.tts_engine:
                logger.info(f"Generating speech using local TTS engine with voice: {voice} for language: {language}")
                result = self._generate_local_speech(text, voice, language)
                if result:
                    logger.info(f"Successfully generated audio: {safe_len(result)} bytes")
                    return result
                else:
                    logger.warning("Local TTS returned no audio data")
                    return None
            else:
                logger.warning("No local TTS engine available")
                return None
                
        except Exception as e:
            logger.error(f"Error generating speech with alternative service: {e}")
            return None
    
    def generate_speech_with_speed(self, text: str, voice: str = "Lisa", 
                                   language: str = "en", speed: str = "normal") -> Optional[bytes]:
        """Generate speech audio with specific speed settings"""
        original_rate = 175.0  # Default rate as float
        try:
            logger.info(f"Generating speech with speed={speed} for {safe_len(text)} characters")
            
            # Try enhanced TTS with speed control for better results
            if self.enhanced_tts and language in self.supported_languages:
                # Map speed options to numerical values
                speed_mapping = {
                    "slow": 0.7,
                    "normal": 1.0,
                    "fast": 1.3,
                    "very_fast": 1.6
                }
                speed_value = speed_mapping.get(speed, 1.0)
                
                logger.info(f"Using enhanced TTS with speed control: {speed_value}")
                if TTSConfig:
                    config = TTSConfig(
                        text=text,
                        language=language,
                        speed=speed_value
                    )
                    result = self.enhanced_tts.generate_speech(config)
                    if result:
                        logger.info(f"Successfully generated audio using enhanced TTS with speed: {safe_len(result)} bytes")
                        return result
                    else:
                        logger.warning("Enhanced TTS with speed control failed, using traditional method")
            
            # Map speed options to numerical values for traditional method
            speed_mapping = {
                "slow": 100,      # words per minute
                "normal": 175,    # words per minute
                "fast": 250,      # words per minute
                "very_fast": 300  # words per minute
            }
            
            # Get the base rate
            base_rate = speed_mapping.get(speed, 175)
            
            # For Tamil, adjust the rate to be more appropriate
            if language == "ta":
                # Tamil needs slower speech for clarity
                if speed == "slow":
                    base_rate = 120
                elif speed == "normal":
                    base_rate = 150
                elif speed == "fast":
                    base_rate = 180
                else:  # very_fast
                    base_rate = 200
            
            # Store the original rate
            if self.tts_engine:
                rate_value = self.tts_engine.getProperty('rate')
                if isinstance(rate_value, (int, float)):
                    original_rate = float(rate_value)
                # else keep the default rate
            
            # Set the new rate
            if self.tts_engine:
                self.tts_engine.setProperty('rate', float(base_rate))
                logger.info(f"Set speech rate to {base_rate} WPM for {speed} speed")
            
            # Generate the speech
            result = self.generate_speech(text, voice, language)
            
            # Restore the original rate
            if self.tts_engine:
                self.tts_engine.setProperty('rate', original_rate)
                logger.info("Restored original speech rate")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating speech with speed control: {e}")
            # Try to restore original rate even if there was an error
            try:
                if self.tts_engine:
                    self.tts_engine.setProperty('rate', original_rate)
            except:
                pass
            return None
    
    def _preprocess_tamil_for_local_tts(self, text: str) -> str:
        """Enhanced preprocessing for Tamil text to improve local TTS quality"""
        if not text:
            return text
            
        # Apply the standard Indic preprocessing first
        processed_text = self._preprocess_indic_text(text, "ta")
        
        # Additional Tamil-specific enhancements using safe string operations
        # Add more pauses for complex Tamil sentences
        processed_text = processed_text.replace('. ', '. ###PAUSE### ###PAUSE### ')
        processed_text = processed_text.replace('? ', '? ###PAUSE### ###PAUSE### ')
        processed_text = processed_text.replace('! ', '! ###PAUSE### ###PAUSE### ')
        
        # Handle common Tamil sentence patterns and structures with string replacement
        # Add pauses around conjunctions
        tamil_conjunctions = [
            'மற்றும்',  # and
            'ஆனால்',   # but
            'எனவே',    # therefore
            'ஆகவே',    # hence
            'இதனால்',   # by this
            'அதனால்'    # therefore
        ]
        
        for conj in tamil_conjunctions:
            processed_text = processed_text.replace(f' {conj} ', f' ###PAUSE### {conj} ###PAUSE### ')
        
        # Add short pauses around common particles
        tamil_particles = [
            'உம்',     # also
            'ஆகிய',    # called
            'போன்ற',   # like
            'என்பது',   # that is
            'என்று'    # said that
        ]
        
        for particle in tamil_particles:
            processed_text = processed_text.replace(f' {particle} ', f' ###SHORTPAUSE### {particle} ###SHORTPAUSE### ')
        
        # Normalize spacing carefully to preserve Tamil characters
        import re
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        logger.info(f"Enhanced Tamil preprocessing applied: {processed_text[:150]}...")
        return processed_text
    
    def _generate_cloud_tts(self, text: str, voice: str, language: str, audio_format: str) -> Optional[bytes]:
        """Generate speech using cloud-based TTS services for better quality"""
        try:
            # Try Google Cloud TTS first
            gTTS_result = self._generate_google_cloud_tts(text, voice, language, audio_format)
            if gTTS_result:
                return gTTS_result
            
            # If Google Cloud TTS fails, try other cloud services
            return None
        except Exception as e:
            logger.warning(f"Cloud TTS generation failed: {e}")
            return None
    
    def _generate_google_cloud_tts(self, text: str, voice: str, language: str, audio_format: str) -> Optional[bytes]:
        """Generate speech using Google Cloud TTS with enhanced options"""
        max_retries = 3
        try:
            # This will only be called if GttsAvailable is True
            if not GttsAvailable or gTTS is None:
                return None
            
            # Map language codes for gTTS
            language_mapping = {
                "ta": "ta",  # Tamil
                "hi": "hi",  # Hindi
                "en": "en",
                "es": "es",
                "fr": "fr",
                "de": "de",
                "it": "it",
                "pt": "pt",
                "ru": "ru",
                "ja": "ja",
                "ko": "ko",
                "zh": "zh-CN"
            }
            
            tts_language = language_mapping.get(language, "en")
            
            # Enhanced preprocessing for Tamil before sending to cloud TTS
            processed_text = text
            if language == "ta":
                processed_text = self._preprocess_tamil_for_cloud_tts(text)
            
            # Try multiple Tamil voices for better quality
            tamil_voices = ['ta', 'ta-in'] if language == "ta" else [tts_language]
            
            # Retry logic for cloud TTS
            last_exception = None
            
            for attempt in range(max_retries):
                for tts_voice in tamil_voices:
                    try:
                        # Create gTTS object with optimized settings for better quality
                        tts_params = {
                            'text': processed_text,
                            'lang': tts_voice,
                            'slow': False,
                            'lang_check': False
                        }
                        
                        # For Tamil, use specific settings for better pronunciation
                        if language == "ta":
                            tts_params['slow'] = True  # Slower speech for better clarity in Tamil
                            tts_params['lang_check'] = True  # Enable language checking for Tamil
                        
                        tts = gTTS(**tts_params)
                        
                        # Save to bytes with timeout handling
                        audio_buffer = io.BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)
                        
                        audio_data = audio_buffer.read()
                        if audio_data and len(audio_data) > 0:
                            logger.info(f"Generated Google Cloud TTS audio with voice '{tts_voice}': {len(audio_data)} bytes")
                            return audio_data
                        else:
                            logger.warning(f"Google Cloud TTS with voice '{tts_voice}' returned no audio data")
                    except Exception as e:
                        last_exception = e
                        logger.warning(f"Google Cloud TTS attempt {attempt + 1} with voice '{tts_voice}' failed: {e}")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(0.5)  # Brief delay before retry
            
            if last_exception:
                raise last_exception
                
        except Exception as e:
            logger.warning(f"Google Cloud TTS generation failed after {max_retries} attempts: {e}")
            return None
    
    def _preprocess_tamil_for_cloud_tts(self, text: str) -> str:
        """Enhanced preprocessing for Tamil text to improve cloud TTS quality"""
        if not text:
            return text
            
        # Use the improved Indic preprocessing first
        processed_text = self._preprocess_indic_text(text, "ta")
        
        # Add additional cloud-specific enhancements for Tamil
        # Add pauses around common Tamil conjunctions for better prosody
        tamil_conjunctions = [
            'மற்றும்',  # and
            'ஆனால்',   # but
            'எனவே',    # therefore
            'ஆகவே',    # hence
            'இதனால்',   # by this
            'அதனால்'    # therefore
        ]
        
        for conj in tamil_conjunctions:
            processed_text = processed_text.replace(f' {conj} ', f' ###PAUSE### {conj} ###PAUSE### ')
        
        # Add short pauses around common particles
        tamil_particles = [
            'உம்',     # also
            'ஆகிய',    # called
            'போன்ற',   # like
            'என்பது',   # that is
            'என்று'    # said that
        ]
        
        for particle in tamil_particles:
            processed_text = processed_text.replace(f' {particle} ', f' ###SHORTPAUSE### {particle} ###SHORTPAUSE### ')
        
        # Normalize spacing carefully
        import re
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        logger.info(f"Tamil text preprocessed for cloud TTS: {processed_text[:150]}...")
        return processed_text
    
    def _preprocess_indic_text(self, text: str, language: str) -> str:
        """Preprocess Indic languages (like Tamil, Hindi) for better TTS synthesis"""
        if not text or language not in ["ta", "hi"]:
            return text
            
        # Work with the original text to preserve Indic characters
        processed_text = text
        
        # Add pauses after sentence endings using careful character-by-character processing
        result_chars = []
        for char in processed_text:
            result_chars.append(char)
            # Add pause after sentence ending punctuation
            if char in '.!?':
                result_chars.append(' ###PAUSE### ')
        
        processed_text = ''.join(result_chars)
        
        # Handle common Indic conjunctions and particles based on language
        if language == "ta":  # Tamil
            # Use string replacement to preserve Tamil characters
            # Process each particle individually to be safe
            particles = [
                (' உம் ', ' ###SHORTPAUSE### உம் ###SHORTPAUSE### '),
                (' ஆகிய ', ' ###SHORTPAUSE### ஆகிய ###SHORTPAUSE### '),
                (' போன்ற ', ' ###SHORTPAUSE### போன்ற ###SHORTPAUSE### '),
                (' என்பது ', ' ###SHORTPAUSE### என்பது ###SHORTPAUSE### '),
                (' என்று ', ' ###SHORTPAUSE### என்று ###SHORTPAUSE### ')
            ]
        elif language == "hi":  # Hindi
            particles = [
                (' है ', ' ###SHORTPAUSE### है ###SHORTPAUSE### '),
                (' था ', ' ###SHORTPAUSE### था ###SHORTPAUSE### '),
                (' थे ', ' ###SHORTPAUSE### थे ###SHORTPAUSE### '),
                (' हूँ ', ' ###SHORTPAUSE### हूँ ###SHORTPAUSE### '),
                (' होना ', ' ###SHORTPAUSE### होना ###SHORTPAUSE### ')
            ]
        else:
            particles = []
            
        for original, replacement in particles:
            processed_text = processed_text.replace(original, replacement)
            
        # Handle vowel combinations that might be difficult for TTS
        if language == "ta":
            # Be very conservative with Tamil vowel combinations to preserve characters
            # Only handle the most problematic ones with simple replacements
            combinations = [
                ('க்ஷ', 'க் ஷ'),
                ('ஜ்ஞ', 'ஜ் ஞ')
            ]
        elif language == "hi":
            combinations = [
                ('क्ष', 'क् ष'),
                ('ज्ञ', 'ज् ञ'),
                ('श्री', 'श् री')
            ]
        else:
            combinations = []
        
        for original, replacement in combinations:
            processed_text = processed_text.replace(original, replacement)
        
        # Normalize spacing carefully
        import re
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        language_name = self.extended_languages.get(language, language) if language in self.extended_languages else self.supported_languages.get(language, language)
        logger.info(f"Preprocessed Indic text for {language_name}: {processed_text[:100]}...")
        return processed_text
    
    def _preprocess_rtl_text(self, text: str, language: str) -> str:
        """Preprocess right-to-left languages (like Arabic) for better TTS synthesis"""
        if not text or language != "ar":
            return text
            
        import re
        
        # Add pauses for Arabic text
        text = re.sub(r'([.!?])', r'\1 ###PAUSE### ', text)
        
        # Handle common Arabic conjunctions
        arabic_particles = ['و', 'ف', 'ل', 'ب', 'ك']  # waw, fa, lam, ba, kaf
        for particle in arabic_particles:
            text = text.replace(particle, f' ###SHORTPAUSE### {particle}')
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.info(f"Preprocessed RTL text for Arabic: {text[:100]}...")
        return text
    
    def _preprocess_asian_text(self, text: str, language: str) -> str:
        """Preprocess Asian languages (like Thai, Vietnamese) for better TTS synthesis"""
        if not text or language not in ["th", "vi"]:
            return text
            
        import re
        
        # Add pauses for Asian languages
        text = re.sub(r'([.!?])', r'\1 ###PAUSE### ', text)
        
        # For Thai, handle tone markers and vowel arrangements
        if language == "th":
            # Add pauses around Thai-specific punctuation
            text = re.sub(r'([๚๛])', r' ###PAUSE### \1 ###PAUSE### ', text)
        
        # For Vietnamese, handle tone marks
        elif language == "vi":
            # Add pauses around Vietnamese-specific punctuation
            text = re.sub(r'([“”])', r' ###PAUSE### \1 ###PAUSE### ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        language_name = self.extended_languages.get(language, language) if language in self.extended_languages else self.supported_languages.get(language, language)
        logger.info(f"Preprocessed Asian text for {language_name}: {text[:100]}...")
        return text
    
    def _generate_local_speech(self, text: str, voice: str, language: str = "en") -> Optional[bytes]:
        """Generate speech using local pyttsx3 engine with enhanced optimizations"""
        if not self.tts_engine:
            return None
            
        temp_path = None
        try:
            # Preprocess text for specific languages
            processed_text = text
            if language in self.supported_languages or language in self.extended_languages:
                logger.warning(f"Language '{self.supported_languages.get(language, self.extended_languages.get(language, language))}' ({language}) has limited system support which may result in poor audio quality")
                
                # Apply language-specific preprocessing
                if language in ["ta", "hi"]:  # Indic languages
                    if language == "ta":
                        # Use enhanced preprocessing for Tamil
                        processed_text = self._preprocess_tamil_for_local_tts(text)
                    else:
                        processed_text = self._preprocess_indic_text(text, language)
                elif language == "ar":  # RTL languages
                    processed_text = self._preprocess_rtl_text(text, language)
                elif language in ["th", "vi"]:  # Asian languages
                    processed_text = self._preprocess_asian_text(text, language)
                
                logger.info(f"Using preprocessed text for {self.supported_languages.get(language, self.extended_languages.get(language, language))} TTS")
            
            logger.info(f"Generating local speech for {safe_len(processed_text)} characters with voice={voice}, language={language}")
            
            # Configure voice settings based on language
            voices = self.tts_engine.getProperty('voices')
            voice_mapping = self._map_voice_to_system(voice, voices, language)
            
            if voice_mapping:
                self.tts_engine.setProperty('voice', voice_mapping)
                logger.info(f"Set voice to: {voice_mapping}")
            else:
                logger.warning("No suitable voice found, using default")
            
            # Set speech rate and volume with language-specific optimizations
            self.tts_engine.setProperty('rate', 175)  # words per minute
            self.tts_engine.setProperty('volume', 0.8)
            
            # For limited support languages, try to optimize
            if language in self.supported_languages or language in self.extended_languages:
                # Adjust settings for better pronunciation clarity
                rate = 150  # Slower for better clarity
                volume = 0.9  # Slightly higher volume
                
                # Tamil-specific optimizations
                if language == "ta":
                    rate = 140  # Even slower for Tamil
                    volume = 1.0  # Maximum volume for clarity
                    logger.info("Applying Tamil-specific TTS optimizations")
                
                self.tts_engine.setProperty('rate', rate)
                self.tts_engine.setProperty('volume', volume)
                logger.info(f"Adjusted TTS settings for {self.supported_languages.get(language, self.extended_languages.get(language, language))} language - Rate: {rate}, Volume: {volume}")
            
            # Enhanced retry logic for local TTS with multiple attempts
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_path = temp_file.name
                        logger.info(f"Created temporary file: {temp_path}")
                    
                    # Use the save_to_file method and runAndWait to generate the audio
                    logger.info("Starting audio generation...")
                    self.tts_engine.save_to_file(processed_text, temp_path)  # Use processed text
                    self.tts_engine.runAndWait()
                    logger.info("Audio generation completed")
                    
                    # Check if file was created successfully
                    if os.path.exists(temp_path):
                        break
                    else:
                        logger.warning(f"Temporary file not created on attempt {attempt + 1}")
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"Audio generation attempt {attempt + 1} failed: {e}")
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    temp_path = None
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(0.5)
            
            # Read the generated audio file
            if temp_path and os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path)
                logger.info(f"Temporary file size: {file_size} bytes")
                
                with open(temp_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                logger.info(f"Read {safe_len(audio_data)} bytes from temporary file")
                
                # Clean up temporary file
                os.unlink(temp_path)
                logger.info("Temporary file cleaned up")
                
                if audio_data and isinstance(audio_data, bytes) and safe_len(audio_data) > 0:
                    logger.info(f"Local audio generated successfully: {safe_len(audio_data)} bytes")
                    # Check if audio is too small for the text length (indicating a problem)
                    if safe_len(audio_data) < 100 and safe_len(text) > 50:
                        logger.warning(f"Generated audio is unusually small ({safe_len(audio_data)} bytes) for text length {safe_len(text)}")
                        logger.warning("This may indicate the TTS engine cannot properly synthesize the language")
                        # For very small audio in unsupported languages, return None to trigger fallback
                        if (language in self.supported_languages or language in self.extended_languages) and safe_len(audio_data) < 50:
                            logger.warning(f"Audio for {self.supported_languages.get(language, self.extended_languages.get(language, language))} is too small, returning None to trigger fallback")
                            return None
                    return audio_data
                else:
                    logger.error("Audio data is empty")
                    return None
            else:
                logger.error("Temporary file was not created after all attempts")
                return None
            
        except Exception as e:
            logger.error(f"Local TTS generation failed: {e}")
            # Try to clean up temp file if it exists
            try:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
                    logger.info("Temporary file cleaned up after error")
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up temporary file: {cleanup_error}")
            return None
    
    def _map_voice_to_system(self, requested_voice: str, available_voices, language: str = "en") -> Optional[str]:
        """Map requested voice to available system voices, considering language"""
        if not available_voices:
            return None
        
        logger.info(f"Mapping voice '{requested_voice}' for language '{language}'")
        
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
        
        # Language-specific voice preferences
        language_voice_prefs = {
            "es": ["spanish", "es"],
            "fr": ["french", "fr"],
            "de": ["german", "de"],
            "it": ["italian", "it"],
            "pt": ["portuguese", "pt"],
            "hi": ["hindi", "hi"],
            "zh": ["chinese", "zh"],
            "ja": ["japanese", "ja"],
            "ta": ["tamil", "ta", "valluvar"],  # Tamil-specific voices
            "ru": ["russian", "ru"],
            "ar": ["arabic", "ar"],
            "ko": ["korean", "ko"],
            "tr": ["turkish", "tr"],
            "th": ["thai", "th"],
            "vi": ["vietnamese", "vi"],
            "en": ["english", "en", "microsoft"]
        }
        
        requested_prefs = voice_preferences.get(requested_voice, ["female"])
        language_prefs = language_voice_prefs.get(language, [language])
        
        logger.info(f"Requested voice preferences: {requested_prefs}")
        logger.info(f"Language preferences: {language_prefs}")
        
        # Special handling for languages with limited support
        if language in self.extended_languages or language in self.supported_languages:
            language_name = self.extended_languages.get(language, language) if language in self.extended_languages else self.supported_languages.get(language, language)
            logger.info(f"Applying {language_name}-specific voice mapping")
            # Try to find language-specific voices first
            for voice in available_voices:
                voice_id = getattr(voice, 'id', str(voice))
                voice_name = voice_id.lower()
                
                # Look for language-specific keywords
                language_keywords = language_voice_prefs.get(language, [language])
                if any(keyword in voice_name for keyword in language_keywords):
                    logger.info(f"Found {language_name}-specific voice: {voice_id}")
                    return voice_id
        
        # Find best matching voice considering both voice and language
        for voice in available_voices:
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = voice_id.lower()
            logger.info(f"Checking voice: {voice_id}")
            
            # Check for language match first
            language_match = any(lang_pref in voice_name for lang_pref in language_prefs)
            if language_match:
                logger.info(f"Language match found for {voice_id}")
                
                # Then check for voice preference match
                voice_match = any(voice_pref.lower() in voice_name for voice_pref in requested_prefs)
                if voice_match:
                    logger.info(f"Perfect match found: {voice_id}")
                    return voice_id
        
        # If no perfect match, try for language match only
        for voice in available_voices:
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = voice_id.lower()
            
            language_match = any(lang_pref in voice_name for lang_pref in language_prefs)
            if language_match:
                logger.info(f"Language-only match found: {voice_id}")
                return voice_id
        
        # Check for exact voice matches
        for voice in available_voices:
            voice_id = getattr(voice, 'id', str(voice))
            voice_name = voice_id.lower()
            
            # Check for exact matches first
            for pref in requested_prefs:
                if pref.lower() in voice_name:
                    logger.info(f"Mapped {requested_voice} to {voice_id}")
                    return voice_id
        
        # Default to first available voice
        if available_voices:
            default_voice = available_voices[0]
            default_id = getattr(default_voice, 'id', str(default_voice))
            logger.info(f"Using default voice: {default_id}")
            return default_id
            
        logger.warning("No voices available")
        return None
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = "auto") -> Optional[str]:
        """Translate text using Google Translator"""
        if not self.translator_service:
            logger.error("Google Translator service not initialized")
            return None
        
        try:
            # Validate text length
            if safe_len(text) > 50000:
                logger.warning("Text length exceeds translation limit, truncating")
                text = text[:50000] + "..."
            
            # Handle batch translation for long texts
            if safe_len(text) > 5000:
                return self._batch_translate(text, source_language, target_language)
            
            # Map common language codes
            lang_mapping = {
                'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it',
                'pt': 'pt', 'ru': 'ru', 'ja': 'ja', 'ko': 'ko', 'zh': 'zh',
                'ar': 'ar', 'hi': 'hi', 'nl': 'nl', 'sv': 'sv', 'no': 'no',
                'da': 'da', 'fi': 'fi', 'pl': 'pl', 'tr': 'tr', 'th': 'th',
                'ta': 'ta'
            }
            
            source = lang_mapping.get(source_language, source_language)
            target = lang_mapping.get(target_language, target_language)
            
            # Translate text with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Create translator instance for this translation
                    from deep_translator import GoogleTranslator
                    translator = GoogleTranslator(source=source, target=target)
                    translated = translator.translate(text)
                    
                    if translated:
                        logger.info(f"Successfully translated {safe_len(text)} characters from {source} to {target}")
                        return translated
                    else:
                        logger.error("No translation returned")
                        return None
                        
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Translation attempt {attempt + 1} failed, retrying: {e}")
                        continue
                    else:
                        raise e
                
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return None
    
    def _batch_translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Handle translation of long texts by splitting into chunks"""
        try:
            # Split text into sentences
            sentences = text.split('. ')
            translated_sentences = []
            
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Initialize current_chunk
            current_chunk = ""
            
            for sentence in sentences:
                # Add sentence to current chunk if it doesn't exceed limit
                if safe_len(current_chunk + sentence) < 4000:
                    current_chunk += sentence + ". "
                else:
                    # Translate current chunk
                    if current_chunk:
                        chunk_translation = translator.translate(current_chunk.strip())
                        if chunk_translation:
                            translated_sentences.append(chunk_translation)
                    
                    # Start new chunk
                    current_chunk = sentence + ". "
            
            # Translate remaining chunk
            if current_chunk:
                chunk_translation = translator.translate(current_chunk.strip())
                if chunk_translation:
                    translated_sentences.append(chunk_translation)
            
            # Combine all translated chunks
            result = ' '.join(translated_sentences)
            return result if result else None
            
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            return None
    
    def rewrite_with_tone(self, text: str, tone: str = "Neutral") -> str:
        """Rewrite text with specified tone using rule-based approach"""
        logger.info(f"Rewriting text with {tone} tone using rule-based approach")
        
        if tone == "Suspenseful":
            return self._make_suspenseful(text)
        elif tone == "Inspiring":
            return self._make_inspiring(text)
        else:  # Neutral
            return self._make_neutral(text)
    
    def _make_suspenseful(self, text: str) -> str:
        """Transform text to be more suspenseful"""
        # Split into sentences for processing
        sentences = text.split('.')
        rewritten_sentences = []
        
        suspense_words = {
            'said': 'whispered',
            'went': 'crept',
            'looked': 'peered',
            'walked': 'stalked',
            'opened': 'slowly opened',
            'closed': 'slammed shut',
            'appeared': 'emerged from the shadows',
            'happened': 'unfolded ominously',
            'found': 'discovered',
            'saw': 'glimpsed',
            'heard': 'detected',
            'came': 'approached',
            'left': 'vanished'
        }
        
        for sentence in sentences:
            if sentence.strip():
                sentence = sentence.strip()
                
                # Replace words with more suspenseful alternatives
                for normal, suspenseful in suspense_words.items():
                    sentence = sentence.replace(f' {normal} ', f' {suspenseful} ')
                    sentence = sentence.replace(f' {normal.capitalize()} ', f' {suspenseful.capitalize()} ')
                
                # Add atmospheric elements
                if safe_len(sentence) > 50:
                    if 'night' not in sentence.lower() and 'dark' not in sentence.lower():
                        sentence = sentence + "... in the gathering darkness"
                
                # Add suspenseful transitions
                if safe_len(rewritten_sentences) > 0:
                    transitions = ['Suddenly, ', 'Without warning, ', 'In that moment, ', 'Then, ']
                    if not any(sentence.startswith(t) for t in transitions):
                        transitions_len = safe_len(transitions)
                        if transitions_len > 0:
                            sentence = transitions[safe_len(rewritten_sentences) % transitions_len] + sentence.lower()
                
                rewritten_sentences.append(sentence)
        
        result = '. '.join(rewritten_sentences)
        if result and not result.endswith('.'):
            result += '.'
        
        return result
    
    def _make_inspiring(self, text: str) -> str:
        """Transform text to be more inspiring"""
        sentences = text.split('.')
        rewritten_sentences = []
        
        inspiring_words = {
            'said': 'declared',
            'went': 'journeyed',
            'tried': 'strived',
            'worked': 'dedicated themselves',
            'did': 'accomplished',
            'made': 'created',
            'got': 'achieved',
            'found': 'discovered',
            'saw': 'witnessed',
            'came': 'arrived triumphantly',
            'finished': 'completed successfully',
            'started': 'embarked upon',
            'learned': 'mastered',
            'grew': 'flourished'
        }
        
        for sentence in sentences:
            if sentence.strip():
                sentence = sentence.strip()
                
                # Replace words with more inspiring alternatives
                for normal, inspiring in inspiring_words.items():
                    sentence = sentence.replace(f' {normal} ', f' {inspiring} ')
                    sentence = sentence.replace(f' {normal.capitalize()} ', f' {inspiring.capitalize()} ')
                
                # Add motivational elements
                if 'success' not in sentence.lower() and 'achieve' not in sentence.lower():
                    if safe_len(sentence) > 40:
                        sentence = sentence + ", proving that determination leads to success"
                
                # Add inspiring transitions
                if safe_len(rewritten_sentences) > 0:
                    transitions = ['Furthermore, ', 'Moreover, ', 'Additionally, ', 'What\'s more, ']
                    if not any(sentence.startswith(t) for t in transitions):
                        transitions_len = safe_len(transitions)
                        if transitions_len > 0:
                            sentence = transitions[safe_len(rewritten_sentences) % transitions_len] + sentence.lower()
                
                rewritten_sentences.append(sentence)
        
        result = '. '.join(rewritten_sentences)
        if result and not result.endswith('.'):
            result += '.'
        
        return result
    
    def _make_neutral(self, text: str) -> str:
        """Clean and normalize text for neutral tone"""
        sentences = text.split('.')
        rewritten_sentences = []
        
        # Clean up excessive punctuation and formatting
        for sentence in sentences:
            if sentence.strip():
                sentence = sentence.strip()
                
                # Remove excessive exclamation marks
                sentence = sentence.replace('!!!', '.')
                sentence = sentence.replace('!!', '.')
                
                # Normalize capitalization
                sentence = sentence[0].upper() + sentence[1:] if sentence else ""
                
                # Clean up spacing
                sentence = ' '.join(sentence.split())
                
                rewritten_sentences.append(sentence)
        
        result = '. '.join(rewritten_sentences)
        if result and not result.endswith('.'):
            result += '.'
        
        return result
