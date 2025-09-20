#!/usr/bin/env python3
"""
EchoVerse Text Processing Service
Handles text rewriting and analysis with alternative processing
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class EchoVerseTextService:
    """Service for text processing and rewriting in EchoVerse"""
    
    def __init__(self):
        self.alternative_service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the text service with alternative processing"""
        try:
            from services.alternative_service import AlternativeService
            self.alternative_service = AlternativeService()
            logger.info("Alternative text service initialized")
        except ImportError:
            logger.warning("Alternative service not available, using fallback processing")
        except Exception as e:
            logger.warning(f"Alternative service initialization failed: {e}")
    
    def rewrite_with_tone(self, text: str, tone: str = "Neutral") -> str:
        """Rewrite text with specified tone using alternative service or fallback"""
        # Try alternative service first
        if self.alternative_service:
            try:
                rewritten = self.alternative_service.rewrite_with_tone(text, tone)
                if rewritten:
                    logger.info(f"Text rewritten using alternative service with {tone} tone")
                    return rewritten
            except Exception as e:
                logger.error(f"Alternative rewriting failed: {e}")
        
        # Fallback to local rule-based rewriting
        logger.info(f"Using fallback text rewriting with {tone} tone")
        return self._fallback_rewrite(text, tone)
    
    def _fallback_rewrite(self, text: str, tone: str) -> str:
        """Fallback text rewriting using rule-based approach"""
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
                if len(sentence) > 50:
                    if 'night' not in sentence.lower() and 'dark' not in sentence.lower():
                        sentence = sentence + "... in the gathering darkness"
                
                # Add suspenseful transitions
                if len(rewritten_sentences) > 0:
                    transitions = ['Suddenly, ', 'Without warning, ', 'In that moment, ', 'Then, ']
                    if not any(sentence.startswith(t) for t in transitions):
                        sentence = transitions[len(rewritten_sentences) % len(transitions)] + sentence.lower()
                
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
                    if len(sentence) > 40:
                        sentence = sentence + ", proving that determination leads to success"
                
                # Add inspiring transitions
                if len(rewritten_sentences) > 0:
                    transitions = ['Furthermore, ', 'Moreover, ', 'Additionally, ', 'What\'s more, ']
                    if not any(sentence.startswith(t) for t in transitions):
                        sentence = transitions[len(rewritten_sentences) % len(transitions)] + sentence.lower()
                
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
    
    def analyze_text_stats(self, text: str) -> Dict[str, Any]:
        """Analyze text statistics"""
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'character_count': len(text),
            'average_words_per_sentence': len(words) / max(1, len([s for s in sentences if s.strip()])),
            'estimated_reading_time_minutes': len(words) / 200,  # 200 WPM average
            'estimated_audio_duration_minutes': len(words) / 150  # 150 WPM for speech
        }
    
    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """Validate text input and provide feedback"""
        issues = []
        recommendations = []
        
        if not text or not text.strip():
            issues.append("No text provided")
            return {'valid': False, 'issues': issues, 'recommendations': recommendations}
        
        # Check text length
        char_count = len(text)
        if char_count > 100000:
            issues.append("Text is extremely long")
            recommendations.append("Consider breaking text into chapters or sections")
        elif char_count < 10:
            issues.append("Text is very short")
            recommendations.append("Add more content for better results")
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        if exclamation_count > 20:
            issues.append("Excessive exclamation marks")
            recommendations.append("Consider reducing exclamation marks for better audio flow")
        
        # Estimate stats
        word_count = len(text.split())
        estimated_reading_time = word_count / 200  # 200 WPM average
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'recommendations': recommendations,
            'stats': {
                'word_count': word_count,
                'character_count': char_count,
                'sentence_count': len([s for s in text.split('.') if s.strip()]),
                'estimated_reading_time_minutes': round(estimated_reading_time, 1),
                'estimated_audio_duration_minutes': round(word_count / 150, 1)  # 150 WPM for speech
            }
        }