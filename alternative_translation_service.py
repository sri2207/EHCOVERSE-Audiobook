#!/usr/bin/env python3
"""
Alternative Translation Service for EchoVerse
Replaces IBM Watson Language Translator with Google Translator
"""

import os
import logging
from typing import Optional, Dict, Any
from deep_translator import GoogleTranslator
import langdetect

logger = logging.getLogger(__name__)

class AlternativeTranslationService:
    """Alternative translation service using Google Translator"""
    
    def __init__(self):
        self.api_key = os.getenv('AUDIOBOOK_API_KEY', 'ap2_c51760e0-4886-4ca9-80e6-287eeb352592')
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize translation service"""
        try:
            # Test Google Translator
            translator = GoogleTranslator(source='en', target='es')
            test_translation = translator.translate("Hello")
            if test_translation:
                logger.info("✅ Google Translator service initialized successfully")
            else:
                logger.warning("⚠️ Google Translator test translation failed")
        except Exception as e:
            logger.error(f"❌ Google Translator initialization failed: {e}")
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = "auto") -> Optional[str]:
        """Translate text using Google Translator"""
        try:
            # Validate text length
            if len(text) > 50000:
                logger.warning("Text length exceeds translation limit, truncating")
                text = text[:50000] + "..."
            
            # Handle batch translation for long texts
            if len(text) > 5000:
                return self._batch_translate(text, source_language, target_language)
            
            # Auto-detect source language if needed
            if source_language == "auto":
                try:
                    detected_lang = langdetect.detect(text)
                    source_language = detected_lang
                    logger.info(f"Auto-detected source language: {source_language}")
                except Exception as e:
                    logger.warning(f"Language detection failed: {e}")
                    source_language = "auto"
            
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
                    translator = GoogleTranslator(source=source, target=target)
                    translated = translator.translate(text)
                    
                    if translated:
                        logger.info(f"Successfully translated {len(text)} characters from {source} to {target}")
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
            
            current_chunk = ""
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            for sentence in sentences:
                # Add sentence to current chunk if it doesn't exceed limit
                if len(current_chunk + sentence) < 4000:
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
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of the given text"""
        try:
            detected_lang = langdetect.detect(text)
            logger.info(f"Detected language: {detected_lang}")
            return detected_lang
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return None