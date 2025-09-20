"""
Service layer for language detection and translation functionality
"""
import re
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class LanguageDetectionResult:
    """Result of language detection"""
    language_code: str
    confidence: float
    language_name: str
    language_flag: str
    is_reliable: bool

@dataclass
class TranslationResult:
    """Result of text translation"""
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    success: bool

class LanguageService:
    """Service for language detection and translation"""
    
    def __init__(self):
        self.langdetect_module = None
        self.googletrans_translator = None
        self.translation_available = False
        self.using_deep_translator = False
        self.supported_languages = self._load_supported_languages()
        self._initialize_translation_services()
    
    def _initialize_translation_services(self):
        """Initialize translation services with fallback strategy"""
        try:
            # First priority: Language detection
            import langdetect as langdetect_module
            self.langdetect_module = langdetect_module
            print("✅ Language detection loaded successfully")
            
            # Second priority: Translation libraries
            try:
                from deep_translator import GoogleTranslator
                self.GoogleTranslator = GoogleTranslator
                self.translation_available = True
                self.using_deep_translator = True
                print("✅ Deep-translator library loaded successfully")
            except ImportError as e:
                print(f"⚠️ Deep-translator not available: {e}")
                try:
                    import googletrans
                    self.googletrans_translator = googletrans.Translator()
                    self.translation_available = True
                    self.using_deep_translator = False
                    print("✅ Googletrans library loaded successfully")
                except ImportError as googletrans_error:
                    print(f"⚠️ Googletrans not available: {googletrans_error}")
                    self.translation_available = False
                    
        except ImportError as e:
            print(f"⚠️ Language detection not available: {e}")
            self.translation_available = False
    
    def _load_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Load supported languages with metadata"""
        return {
            # Major languages
            'en': {'name': 'English', 'flag': '🇺🇸', 'family': 'Germanic'},
            'es': {'name': 'Spanish', 'flag': '🇪🇸', 'family': 'Romance'},
            'fr': {'name': 'French', 'flag': '🇫🇷', 'family': 'Romance'},
            'de': {'name': 'German', 'flag': '🇩🇪', 'family': 'Germanic'},
            'it': {'name': 'Italian', 'flag': '🇮🇹', 'family': 'Romance'},
            'pt': {'name': 'Portuguese', 'flag': '🇵🇹', 'family': 'Romance'},
            'ru': {'name': 'Russian', 'flag': '🇷🇺', 'family': 'Slavic'},
            'zh': {'name': 'Chinese (Simplified)', 'flag': '🇨🇳', 'family': 'Sino-Tibetan'},
            'ja': {'name': 'Japanese', 'flag': '🇯🇵', 'family': 'Japonic'},
            'ko': {'name': 'Korean', 'flag': '🇰🇷', 'family': 'Koreanic'},
            'ar': {'name': 'Arabic', 'flag': '🇸🇦', 'family': 'Semitic'},
            'hi': {'name': 'Hindi', 'flag': '🇮🇳', 'family': 'Indo-Aryan'},
            'ta': {'name': 'Tamil', 'flag': '🇮🇳', 'family': 'Dravidian'},
            'th': {'name': 'Thai', 'flag': '🇹🇭', 'family': 'Tai-Kadai'},
            'vi': {'name': 'Vietnamese', 'flag': '🇻🇳', 'family': 'Austroasiatic'},
            'nl': {'name': 'Dutch', 'flag': '🇳🇱', 'family': 'Germanic'},
            'sv': {'name': 'Swedish', 'flag': '🇸🇪', 'family': 'Germanic'},
            'no': {'name': 'Norwegian', 'flag': '🇳🇴', 'family': 'Germanic'},
            'da': {'name': 'Danish', 'flag': '🇩🇰', 'family': 'Germanic'},
            'fi': {'name': 'Finnish', 'flag': '🇫🇮', 'family': 'Uralic'},
            'pl': {'name': 'Polish', 'flag': '🇵🇱', 'family': 'Slavic'},
            'tr': {'name': 'Turkish', 'flag': '🇹🇷', 'family': 'Turkic'},
            'he': {'name': 'Hebrew', 'flag': '🇮🇱', 'family': 'Semitic'},
            'fa': {'name': 'Persian', 'flag': '🇮🇷', 'family': 'Indo-Iranian'},
            'uk': {'name': 'Ukrainian', 'flag': '🇺🇦', 'family': 'Slavic'},
            'cs': {'name': 'Czech', 'flag': '🇨🇿', 'family': 'Slavic'},
            'hu': {'name': 'Hungarian', 'flag': '🇭🇺', 'family': 'Uralic'},
            'ro': {'name': 'Romanian', 'flag': '🇷🇴', 'family': 'Romance'},
            'bg': {'name': 'Bulgarian', 'flag': '🇧🇬', 'family': 'Slavic'},
            'hr': {'name': 'Croatian', 'flag': '🇭🇷', 'family': 'Slavic'},
            'sk': {'name': 'Slovak', 'flag': '🇸🇰', 'family': 'Slavic'},
            'sl': {'name': 'Slovenian', 'flag': '🇸🇮', 'family': 'Slavic'},
            'et': {'name': 'Estonian', 'flag': '🇪🇪', 'family': 'Uralic'},
            'lv': {'name': 'Latvian', 'flag': '🇱🇻', 'family': 'Baltic'},
            'lt': {'name': 'Lithuanian', 'flag': '🇱🇹', 'family': 'Baltic'},
            'el': {'name': 'Greek', 'flag': '🇬🇷', 'family': 'Hellenic'},
            'id': {'name': 'Indonesian', 'flag': '🇮🇩', 'family': 'Austronesian'},
            'ms': {'name': 'Malay', 'flag': '🇲🇾', 'family': 'Austronesian'},
            'tl': {'name': 'Filipino', 'flag': '🇵🇭', 'family': 'Austronesian'},
            'sw': {'name': 'Swahili', 'flag': '🇰🇪', 'family': 'Niger-Congo'},
            'af': {'name': 'Afrikaans', 'flag': '🇿🇦', 'family': 'Germanic'},
        }
    
    def detect_language(self, text: str, confidence_threshold: float = 0.7) -> LanguageDetectionResult:
        """Detect language of the given text"""
        if not self.langdetect_module:
            return LanguageDetectionResult(
                language_code='en',
                confidence=0.5,
                language_name='English',
                language_flag='🇺🇸',
                is_reliable=False
            )
        
        try:
            # Clean and prepare text
            clean_text = self._clean_text_for_detection(text)
            if len(clean_text) < 10:
                raise ValueError("Text too short for reliable detection")
            
            # Primary detection using langdetect
            detected = self.langdetect_module.detect(clean_text[:2000])
            confidence = 0.8  # Default confidence
            
            # Multi-sample confidence calculation for longer texts
            if len(clean_text) > 1000:
                confidence = self._calculate_confidence(clean_text)
            
            # Validate and normalize language code
            detected = self._normalize_language_code(detected)
            
            # Get language info
            lang_info = self.supported_languages.get(detected, self.supported_languages['en'])
            
            return LanguageDetectionResult(
                language_code=detected,
                confidence=confidence,
                language_name=lang_info['name'],
                language_flag=lang_info['flag'],
                is_reliable=confidence >= confidence_threshold
            )
            
        except Exception as e:
            print(f"Language detection error: {str(e)}")
            return self._fallback_detection(text)
    
    def _clean_text_for_detection(self, text: str) -> str:
        """Clean text for more accurate language detection"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs and email addresses
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.!?]{3,}', '.', text)
        
        return text
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence by testing multiple text segments"""
        # Return low confidence if langdetect module is not available
        if not self.langdetect_module:
            return 0.3
            
        segments = [
            text[:500],
            text[len(text)//4:len(text)//4+500],
            text[len(text)//2:len(text)//2+500],
            text[-500:] if len(text) > 500 else text
        ]
        
        detections = []
        for segment in segments:
            if len(segment.strip()) > 50:
                try:
                    detected = self.langdetect_module.detect(segment)
                    detections.append(detected)
                except:
                    continue
        
        if not detections:
            return 0.3
        
        # Calculate consistency-based confidence
        most_common = max(set(detections), key=detections.count)
        confidence = detections.count(most_common) / len(detections)
        return confidence
    
    def _normalize_language_code(self, lang_code: str) -> str:
        """Normalize language codes to supported format"""
        # Handle Chinese variants
        if lang_code in ['zh-cn', 'zh-hans']:
            return 'zh'
        elif lang_code in ['zh-tw', 'zh-hant']:
            return 'zh-tw'
        
        # Return if supported, otherwise default to English
        return lang_code if lang_code in self.supported_languages else 'en'
    
    def _fallback_detection(self, text: str) -> LanguageDetectionResult:
        """Fallback detection using character patterns"""
        text_sample = text[:1000].lower()
        
        # Character-based detection patterns
        patterns = {
            'zh': r'[\u4e00-\u9fff]',  # Chinese
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # Japanese
            'ko': r'[\uac00-\ud7af]',  # Korean
            'ar': r'[\u0600-\u06ff]',  # Arabic
            'hi': r'[\u0900-\u097f]',  # Hindi
            'ta': r'[\u0b80-\u0bff]',  # Tamil
            'ru': r'[\u0400-\u04ff]',  # Cyrillic
            'th': r'[\u0e00-\u0e7f]',  # Thai
        }
        
        for lang, pattern in patterns.items():
            if re.search(pattern, text_sample):
                lang_info = self.supported_languages[lang]
                return LanguageDetectionResult(
                    language_code=lang,
                    confidence=0.6,
                    language_name=lang_info['name'],
                    language_flag=lang_info['flag'],
                    is_reliable=False
                )
        
        # Default to English
        return LanguageDetectionResult(
            language_code='en',
            confidence=0.3,
            language_name='English',
            language_flag='🇺🇸',
            is_reliable=False
        )
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: Optional[str] = None) -> TranslationResult:
        """Translate text to target language"""
        if not self.translation_available:
            return TranslationResult(
                translated_text=text,
                source_language=source_language or 'unknown',
                target_language=target_language,
                confidence=0.0,
                success=False
            )
        
        try:
            # Auto-detect source language if not provided
            if not source_language:
                detection_result = self.detect_language(text)
                source_language = detection_result.language_code
            
            # Skip translation if source and target are the same
            if source_language == target_language:
                return TranslationResult(
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence=1.0,
                    success=True
                )
            
            # Perform translation
            if self.using_deep_translator:
                translated_text = self._translate_with_deep_translator(
                    text, source_language, target_language
                )
            else:
                translated_text = self._translate_with_googletrans(
                    text, source_language, target_language
                )
            
            return TranslationResult(
                translated_text=translated_text,
                source_language=source_language,
                target_language=target_language,
                confidence=0.8,
                success=True
            )
            
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return TranslationResult(
                translated_text=text,
                source_language=source_language or 'unknown',
                target_language=target_language,
                confidence=0.0,
                success=False
            )
    
    def _translate_with_deep_translator(self, text: str, source: str, target: str) -> str:
        """Translate using deep-translator"""
        translator = self.GoogleTranslator(source=source, target=target)
        return translator.translate(text)
    
    def _translate_with_googletrans(self, text: str, source: str, target: str) -> str:
        """Translate using googletrans"""
        if not self.googletrans_translator:
            raise RuntimeError("Googletrans translator not available")
            
        result = self.googletrans_translator.translate(
            text=text, src=source, dest=target
        )
        return result.text
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get all supported languages"""
        return self.supported_languages
    
    def get_language_families(self) -> Dict[str, list]:
        """Get languages organized by family"""
        families = {}
        for code, info in self.supported_languages.items():
            family = info['family']
            if family not in families:
                families[family] = []
            families[family].append({
                'code': code,
                'name': info['name'],
                'flag': info['flag']
            })
        return families