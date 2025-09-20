#!/usr/bin/env python3
"""
IBM Watson Service Integration for EchoVerse
Handles Text-to-Speech, Language Translator, and Watsonx LLM
With fallback to alternative services when IBM credentials are not provided
"""

import os
import logging
import time
from typing import Optional, Dict, Any
import requests
import json
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class IBMWatsonService:
    """Service for IBM Watson AI integrations with fallback to alternative services"""
    
    def __init__(self):
        self.tts_service = None
        self.translator_service = None
        self.watsonx_service = None
        self.use_alternative_services = os.getenv('USE_ALTERNATIVE_SERVICES', 'false').lower() == 'true'
        
        if not self.use_alternative_services:
            self._initialize_services()
        else:
            logger.info("Using alternative services instead of IBM Watson")
            # Initialize alternative services
            try:
                self.translator_service = GoogleTranslator(source='auto', target='en')
                logger.info("✅ Google Translator service initialized (alternative to IBM Language Translator)")
            except Exception as e:
                logger.warning(f"⚠️ Google Translator initialization failed: {e}")
                self.translator_service = None
    
    def _initialize_services(self):
        """Initialize IBM Watson services with API keys from environment"""
        try:
            # Text-to-Speech Service
            tts_api_key = os.getenv('IBM_TTS_API_KEY')
            tts_url = os.getenv('IBM_TTS_URL', 'https://api.us-south.text-to-speech.watson.cloud.ibm.com')
            
            if tts_api_key:
                try:
                    from ibm_watson import TextToSpeechV1
                    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
                    authenticator = IAMAuthenticator(tts_api_key)
                    self.tts_service = TextToSpeechV1(authenticator=authenticator)
                    self.tts_service.set_service_url(tts_url)
                    logger.info("✅ IBM Text-to-Speech service initialized")
                except ImportError:
                    logger.warning("⚠️ IBM Watson SDK not installed, TTS service unavailable")
                except Exception as e:
                    logger.warning(f"⚠️ IBM TTS service initialization failed: {e}")
            else:
                logger.info("ℹ️ IBM TTS API key not provided, using alternative services")
            
            # Google Translator Service (replacement for deprecated IBM Language Translator)
            try:
                self.translator_service = GoogleTranslator(source='auto', target='en')
                logger.info("✅ Google Translator service initialized (IBM Language Translator deprecated)")
            except Exception as e:
                logger.warning(f"⚠️ Google Translator initialization failed: {e}")
                self.translator_service = None
            
            # Watsonx.ai Service (for Granite LLM)
            self.watsonx_api_key = os.getenv('IBM_WATSONX_API_KEY')
            self.watsonx_project_id = os.getenv('IBM_WATSONX_PROJECT_ID')
            self.watsonx_url = os.getenv('IBM_WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
            
            if self.watsonx_api_key and self.watsonx_project_id:
                logger.info("✅ Watsonx.ai credentials configured")
            else:
                logger.info("ℹ️ Watsonx.ai credentials not provided, using alternative services")
                
        except Exception as e:
            logger.error(f"❌ Error initializing IBM Watson services: {e}")
    
    def generate_speech(self, text: str, voice: str = "en-US_LisaV3Voice", 
                       audio_format: str = "audio/mp3") -> Optional[bytes]:
        """Generate speech audio using IBM Text-to-Speech"""
        if not self.tts_service:
            logger.info("IBM TTS service not available")
            return None
        
        try:
            # Map friendly voice names to IBM Watson voice IDs
            voice_mapping = {
                "Lisa": "en-US_LisaV3Voice",
                "Michael": "en-US_MichaelV3Voice", 
                "Allison": "en-US_AllisonV3Voice",
                "Kevin": "en-US_KevinV3Voice",
                "Emma": "en-US_EmmaExpressive"
            }
            
            watson_voice = voice_mapping.get(voice, voice)
            
            # Validate text length (IBM TTS has limits)
            if len(text) > 5000:
                logger.warning("Text length exceeds recommended limit, truncating")
                text = text[:5000] + "..."
            
            # Generate audio with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # IBM Watson TTS synthesize returns a DetailedResponse
                    # Call get_result() once to get the audio content (bytes)
                    response = self.tts_service.synthesize(
                        text=text,
                        voice=watson_voice,
                        accept=audio_format
                    )
                    
                    # The audio content is directly in the result as bytes
                    audio_content = response.get_result()
                    
                    if audio_content and isinstance(audio_content, bytes):
                        logger.info(f"Generated audio: {len(audio_content)} bytes")
                        return audio_content
                    else:
                        logger.error("No valid audio content received from TTS service")
                        return None
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"TTS attempt {attempt + 1} failed, retrying: {e}")
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return None
    
    def translate_text(self, text: str, target_language: str, 
                      source_language: str = "en") -> Optional[str]:
        """Translate text using Google Translator (replacement for deprecated IBM Language Translator)"""
        if not self.translator_service:
            logger.error("Google Translator service not initialized")
            return None
        
        try:
            # Validate text length
            if len(text) > 50000:
                logger.warning("Text length exceeds translation limit, truncating")
                text = text[:50000] + "..."
            
            # Handle batch translation for long texts
            if len(text) > 5000:
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
                        time.sleep(1)  # Brief delay before retry
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
    
    def rewrite_with_granite(self, text: str, tone: str) -> Optional[str]:
        """Rewrite text using IBM Watsonx Granite LLM"""
        if not self.watsonx_api_key or not self.watsonx_project_id:
            logger.info("Watsonx.ai credentials not available for text rewriting")
            return None
        
        try:
            # Granite LLM prompt engineering for tone rewriting
            tone_prompts = {
                "Neutral": "Rewrite the following text in a clear, balanced, and professional tone suitable for informational content:",
                "Suspenseful": "Rewrite the following text in a mysterious, tension-building tone perfect for thrillers and mysteries:",
                "Inspiring": "Rewrite the following text in an uplifting, motivational tone that energizes and encourages readers:"
            }
            
            prompt = f"{tone_prompts.get(tone, tone_prompts['Neutral'])}\n\n{text}"
            
            # IBM Watsonx.ai API call
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.watsonx_api_key}'
            }
            
            payload = {
                "model_id": "ibm/granite-13b-chat-v2",
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 2048,
                    "min_new_tokens": 0,
                    "stop_sequences": [],
                    "repetition_penalty": 1
                },
                "project_id": self.watsonx_project_id
            }
            
            response = requests.post(
                f"{self.watsonx_url}/ml/v1-beta/generation/text",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'results' in result and len(result['results']) > 0:
                    rewritten_text = result['results'][0]['generated_text']
                    logger.info(f"Text rewritten using IBM Watsonx Granite LLM with {tone} tone")
                    return rewritten_text
            
            logger.error(f"Watsonx API call failed with status {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error rewriting text with Granite LLM: {e}")
            return None
    
    def get_available_voices(self) -> list:
        """Get list of available voices from IBM Watson TTS"""
        if not self.tts_service:
            return []
        
        try:
            response = self.tts_service.list_voices().get_result()
            if response and isinstance(response, dict):
                return response.get('voices', [])
            return []
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []