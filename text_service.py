"""
Service layer for text processing and analysis functionality
"""
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class EmotionType(Enum):
    """Emotion types for text analysis"""
    NEUTRAL = "neutral"
    EXCITEMENT = "excitement"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    JOY = "joy"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    ACTION = "action"

@dataclass
class EmotionAnalysis:
    """Result of emotion analysis"""
    dominant_emotion: EmotionType
    intensity: float
    emotion_scores: Dict[str, int]
    confidence: float

@dataclass
class TextAnalysis:
    """Comprehensive text analysis result"""
    word_count: int
    sentence_count: int
    paragraph_count: int
    reading_level: str
    genre_hints: List[str]
    themes: List[Dict[str, Any]]
    characters: List[str]
    emotion_analysis: EmotionAnalysis

class TextProcessingService:
    """Service for text processing and analysis"""
    
    def __init__(self):
        self.emotion_keywords = self._load_emotion_keywords()
        self.genre_keywords = self._load_genre_keywords()
        self.theme_keywords = self._load_theme_keywords()
    
    def _load_emotion_keywords(self) -> Dict[str, List[str]]:
        """Load emotion detection keywords"""
        return {
            'excitement': [
                'excited', 'amazing', 'wonderful', 'fantastic', 'incredible', 
                'awesome', 'brilliant', 'marvelous', 'spectacular', 'thrilling',
                'exhilarating', 'electrifying', '!', 'wow', 'yes'
            ],
            'sadness': [
                'sad', 'tragic', 'sorrow', 'grief', 'melancholy', 'tears',
                'crying', 'depressed', 'heartbroken', 'mourning', 'lonely',
                'devastated', 'miserable', 'despair', 'anguish'
            ],
            'anger': [
                'angry', 'furious', 'rage', 'mad', 'annoyed', 'irritated',
                'frustrated', 'outraged', 'livid', 'enraged', 'incensed',
                'hostile', 'aggressive', 'violent', 'hatred'
            ],
            'fear': [
                'scared', 'frightened', 'terrified', 'afraid', 'panic', 'horror',
                'anxious', 'worried', 'nervous', 'alarmed', 'startled',
                'petrified', 'trembling', 'shaking', 'dread'
            ],
            'joy': [
                'happy', 'joyful', 'cheerful', 'delighted', 'pleased', 'glad',
                'ecstatic', 'blissful', 'content', 'satisfied', 'elated',
                'overjoyed', 'jubilant', 'euphoric', 'radiant'
            ],
            'mystery': [
                'mysterious', 'strange', 'eerie', 'unknown', 'secret', 'hidden',
                'enigmatic', 'puzzling', 'cryptic', 'suspicious', 'shadowy',
                'obscure', 'unexplained', 'bizarre', 'peculiar'
            ],
            'romance': [
                'love', 'romantic', 'heart', 'kiss', 'tender', 'affection',
                'passion', 'intimate', 'beloved', 'darling', 'sweetheart',
                'embrace', 'caress', 'adoration', 'devotion'
            ],
            'action': [
                'fight', 'battle', 'run', 'chase', 'quick', 'fast', 'suddenly',
                'rushed', 'sprint', 'leap', 'dash', 'hurry', 'urgent',
                'immediate', 'explosive', 'dynamic'
            ]
        }
    
    def _load_genre_keywords(self) -> Dict[str, List[str]]:
        """Load genre detection keywords"""
        return {
            'fantasy': [
                'magic', 'wizard', 'dragon', 'fairy', 'enchanted', 'spell',
                'magical', 'mystical', 'sorcerer', 'witch', 'potion', 'quest',
                'kingdom', 'realm', 'prophecy', 'legend'
            ],
            'science_fiction': [
                'space', 'robot', 'future', 'technology', 'alien', 'time',
                'spaceship', 'galaxy', 'planet', 'android', 'cyborg', 'laser',
                'quantum', 'dimension', 'universe', 'cosmic'
            ],
            'mystery': [
                'detective', 'clue', 'murder', 'investigation', 'suspect',
                'crime', 'evidence', 'mystery', 'solve', 'case', 'police',
                'forensic', 'witness', 'alibi', 'motive'
            ],
            'romance': [
                'love', 'wedding', 'relationship', 'marriage', 'couple',
                'boyfriend', 'girlfriend', 'husband', 'wife', 'date',
                'valentine', 'proposal', 'engagement', 'honeymoon'
            ],
            'horror': [
                'ghost', 'haunted', 'vampire', 'zombie', 'monster', 'demon',
                'supernatural', 'possessed', 'cemetery', 'graveyard',
                'nightmare', 'scream', 'blood', 'terror', 'evil'
            ],
            'adventure': [
                'adventure', 'journey', 'explore', 'discovery', 'expedition',
                'treasure', 'map', 'travel', 'quest', 'voyage', 'wilderness',
                'survival', 'challenge', 'danger', 'rescue'
            ],
            'thriller': [
                'suspense', 'tension', 'chase', 'escape', 'pursuit', 'danger',
                'threat', 'conspiracy', 'betrayal', 'trap', 'assassin',
                'spy', 'intrigue', 'plot', 'scheme'
            ]
        }
    
    def _load_theme_keywords(self) -> Dict[str, List[str]]:
        """Load theme detection keywords"""
        return {
            'family': [
                'family', 'mother', 'father', 'children', 'parent', 'sibling',
                'brother', 'sister', 'grandmother', 'grandfather', 'home',
                'household', 'relatives', 'generation', 'legacy'
            ],
            'friendship': [
                'friend', 'friendship', 'companion', 'buddy', 'pal', 'ally',
                'bond', 'loyalty', 'trust', 'support', 'together',
                'solidarity', 'camaraderie', 'fellowship', 'unity'
            ],
            'growth': [
                'growth', 'development', 'learning', 'education', 'wisdom',
                'maturity', 'progress', 'evolution', 'transformation',
                'improvement', 'advancement', 'achievement', 'success'
            ],
            'conflict': [
                'conflict', 'struggle', 'challenge', 'obstacle', 'problem',
                'difficulty', 'crisis', 'dilemma', 'tension', 'opposition',
                'competition', 'rivalry', 'dispute', 'disagreement'
            ],
            'redemption': [
                'redemption', 'forgiveness', 'second chance', 'redemptive',
                'salvation', 'recovery', 'healing', 'renewal', 'reform',
                'transformation', 'atonement', 'reconciliation'
            ],
            'sacrifice': [
                'sacrifice', 'sacrifice', 'giving up', 'selfless', 'noble',
                'heroic', 'martyrdom', 'devotion', 'dedication', 'commitment',
                'service', 'duty', 'responsibility', 'obligation'
            ]
        }
    
    def analyze_emotion(self, text: str) -> EmotionAnalysis:
        """Analyze emotional content of text"""
        text_lower = text.lower()
        emotion_scores = {}
        
        # Calculate emotion scores
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            emotion_scores[emotion] = score
        
        # Determine dominant emotion
        max_score = max(emotion_scores.values()) if emotion_scores.values() else 0
        
        if max_score == 0:
            dominant_emotion = EmotionType.NEUTRAL
            intensity = 0.0
            confidence = 1.0
        else:
            dominant_emotion_name = max(emotion_scores.keys(), 
                                      key=lambda k: emotion_scores[k])
            dominant_emotion = EmotionType(dominant_emotion_name)
            
            # Calculate intensity (normalized to 0-1)
            intensity = min(max_score / 10, 1.0)
            
            # Calculate confidence based on score distribution
            total_score = sum(emotion_scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.0
        
        return EmotionAnalysis(
            dominant_emotion=dominant_emotion,
            intensity=intensity,
            emotion_scores=emotion_scores,
            confidence=confidence
        )
    
    def analyze_text_comprehensive(self, text: str) -> TextAnalysis:
        """Perform comprehensive text analysis"""
        # Basic metrics
        word_count = len(text.split())
        sentence_count = len(re.findall(r'[.!?]+', text))
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Reading level estimation
        reading_level = self._estimate_reading_level(text, word_count, sentence_count)
        
        # Genre detection
        genre_hints = self._detect_genres(text)
        
        # Theme detection
        themes = self._detect_themes(text)
        
        # Character detection
        characters = self._detect_characters(text)
        
        # Emotion analysis
        emotion_analysis = self.analyze_emotion(text)
        
        return TextAnalysis(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            reading_level=reading_level,
            genre_hints=genre_hints,
            themes=themes,
            characters=characters,
            emotion_analysis=emotion_analysis
        )
    
    def _estimate_reading_level(self, text: str, word_count: int, 
                               sentence_count: int) -> str:
        """Estimate reading difficulty level"""
        if sentence_count == 0:
            return "unknown"
        
        avg_words_per_sentence = word_count / sentence_count
        
        # Count complex words (3+ syllables)
        complex_words = len([word for word in text.split() 
                           if self._count_syllables(word) >= 3])
        complex_word_ratio = complex_words / word_count if word_count > 0 else 0
        
        # Simple reading level estimation
        if avg_words_per_sentence < 10 and complex_word_ratio < 0.1:
            return "elementary"
        elif avg_words_per_sentence < 15 and complex_word_ratio < 0.15:
            return "middle_school"
        elif avg_words_per_sentence < 20 and complex_word_ratio < 0.25:
            return "high_school"
        else:
            return "college"
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        
        if word[0] in vowels:
            count += 1
        
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        
        if word.endswith('e'):
            count -= 1
        
        if count == 0:
            count += 1
        
        return count
    
    def _detect_genres(self, text: str) -> List[str]:
        """Detect potential genres based on keywords"""
        text_lower = text.lower()
        genre_scores = {}
        
        for genre, keywords in self.genre_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                genre_scores[genre] = score
        
        # Return genres sorted by score
        return sorted(genre_scores.keys(), key=lambda x: genre_scores[x], reverse=True)
    
    def _detect_themes(self, text: str) -> List[Dict[str, Any]]:
        """Detect themes in the text"""
        text_lower = text.lower()
        themes = []
        
        for theme, keywords in self.theme_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                themes.append({
                    'theme': theme,
                    'strength': min(score, 10),
                    'keywords_found': [kw for kw in keywords if kw in text_lower]
                })
        
        # Sort by strength
        return sorted(themes, key=lambda x: x['strength'], reverse=True)
    
    def _detect_characters(self, text: str) -> List[str]:
        """Detect potential character names"""
        # Simple heuristic: look for capitalized words that might be names
        sentences = re.split(r'[.!?]+', text)
        potential_names = set()
        
        common_words = {
            'the', 'and', 'but', 'or', 'so', 'yet', 'for', 'nor', 'a', 'an',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
            'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
            'his', 'her', 'its', 'our', 'their', 'chapter', 'page', 'book'
        }
        
        for sentence in sentences:
            words = sentence.split()
            for word in words:
                # Clean the word
                clean_word = re.sub(r'[^a-zA-Z]', '', word)
                
                # Check if it's a potential name
                if (len(clean_word) > 2 and 
                    clean_word[0].isupper() and 
                    clean_word.lower() not in common_words and
                    clean_word.isalpha()):
                    potential_names.add(clean_word)
        
        # Return up to 10 most likely character names
        return list(potential_names)[:10]
    
    def enhance_text_for_speech(self, text: str, emotion_type: EmotionType, 
                               intensity: float, continuous_flow: bool = True) -> str:
        """Enhance text for natural speech synthesis"""
        if continuous_flow:
            return self._create_continuous_flow(text, emotion_type, intensity)
        else:
            return self._create_traditional_flow(text, emotion_type, intensity)
    
    def _create_continuous_flow(self, text: str, emotion_type: EmotionType, 
                               intensity: float) -> str:
        """Create smooth, continuous speech flow"""
        # Clean up excessive punctuation
        text = re.sub(r'([.!?])\s*([.!?])+', r'\1 ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Replace formal language with natural speech patterns
        natural_replacements = {
            r'\bhowever\b': 'but',
            r'\btherefore\b': 'so',
            r'\bnevertheless\b': 'but still',
            r'\bfurthermore\b': 'and also',
            r'\bmoreover\b': 'plus',
            r'\bin addition\b': 'also',
            r'\bobviously\b': 'clearly',
            r'\bcertainly\b': 'definitely',
            r'\bundoubtedly\b': 'for sure',
        }
        
        for formal, casual in natural_replacements.items():
            text = re.sub(formal, casual, text, flags=re.IGNORECASE)
        
        # Add contractions
        contractions = {
            r'\bit is\b': "it's",
            r'\bthey are\b': "they're",
            r'\byou are\b': "you're",
            r'\bwe are\b': "we're",
            r'\bI am\b': "I'm",
            r'\bdo not\b': "don't",
            r'\bdoes not\b': "doesn't",
            r'\bcannot\b': "can't",
        }
        
        for long_form, contraction in contractions.items():
            text = re.sub(long_form, contraction, text, flags=re.IGNORECASE)
        
        # Apply emotion-specific enhancements
        text = self._apply_emotion_flow(text, emotion_type, intensity)
        
        return text.strip()
    
    def _create_traditional_flow(self, text: str, emotion_type: EmotionType, 
                                intensity: float) -> str:
        """Create traditional speech flow with pauses"""
        sentences = re.split(r'[.!?]+', text)
        enhanced_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            sentence = sentence.strip()
            
            # Add natural breathing pauses for long sentences
            if len(sentence) > 100:
                sentence = re.sub(
                    r'\b(and|but|or|so|yet|for|nor|because|since|although|while|when|where|if|unless)\s+',
                    r'\1... ', sentence
                )
            
            # Apply emotion-specific enhancements
            sentence = self._apply_emotion_flow(sentence, emotion_type, intensity)
            enhanced_sentences.append(sentence)
        
        # Join with appropriate pauses based on emotion intensity
        pause_marker = '.... ' if intensity > 0.7 else '... ' if intensity > 0.3 else '. '
        result = pause_marker.join(enhanced_sentences)
        
        if not result.endswith(('.', '!', '?')):
            result += '.'
        
        return result
    
    def _apply_emotion_flow(self, text: str, emotion_type: EmotionType, 
                           intensity: float) -> str:
        """Apply emotion-specific text modifications"""
        multiplier = max(intensity, 0.3)  # Minimum effect
        
        if emotion_type == EmotionType.EXCITEMENT:
            text = re.sub(r'\b(amazing|incredible|fantastic|wonderful)\b', 
                         r'\1!', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(and then)\b', 'and boom', text, flags=re.IGNORECASE)
            
        elif emotion_type == EmotionType.SADNESS:
            text = re.sub(r'\b(said)\b', 'whispered', text, flags=re.IGNORECASE)
            text = re.sub(r'([.,])\s+', r'\1.... ', text)
            
        elif emotion_type == EmotionType.MYSTERY:
            text = re.sub(r'\b(suddenly)\b', 'out of nowhere', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(appeared)\b', 'emerged from the shadows', text, flags=re.IGNORECASE)
            
        elif emotion_type == EmotionType.ROMANCE:
            text = re.sub(r'\b(looked at)\b', 'gazed into', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(touched)\b', 'caressed', text, flags=re.IGNORECASE)
            
        elif emotion_type == EmotionType.ACTION:
            text = re.sub(r'\b(ran)\b', 'sprinted', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(jumped)\b', 'leaped', text, flags=re.IGNORECASE)
            # Remove pauses for action sequences
            text = re.sub(r'([.!?])\s+', r'\1 ', text)
        
        return text