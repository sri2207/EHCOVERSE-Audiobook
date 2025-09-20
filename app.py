#!/usr/bin/env python3
from flask import Flask, render_template, request, send_file, jsonify, url_for, session
import os
import pyttsx3
import PyPDF2
import docx
from werkzeug.utils import secure_filename
import threading
from datetime import datetime
import uuid
import re
from collections import defaultdict
import hashlib
import json
from werkzeug.security import generate_password_hash, check_password_hash

# API Configuration - Use environment variables for security
API_KEY = os.getenv('AUDIOBOOK_API_KEY', 'ap2_c51760e0-4886-4ca9-80e6-287eeb352592')  # Your API key
API_SERVICE_ENABLED = bool(API_KEY)  # Enable service if API key is available

# Auto-translation configuration
AUTO_DETECT_ENABLED = True
AUTO_TRANSLATE_ENABLED = True
DEFAULT_TARGET_LANGUAGE = 'en'  # Default target language for auto-translation

# Handle translation dependencies with robust fallback
TRANSLATION_AVAILABLE = False
USING_DEEP_TRANSLATOR = False
langdetect_module = None
googletrans_translator = None

# Enhanced import strategy - prioritize deep-translator for compatibility
try:
    # First priority: Language detection (essential)
    import langdetect as langdetect_module
    print("✅ Language detection loaded successfully")
    
    # Second priority: Translation libraries - prefer deep-translator
    try:
        # Try deep-translator first (better compatibility)
        from deep_translator import GoogleTranslator
        TRANSLATION_AVAILABLE = True
        USING_DEEP_TRANSLATOR = True
        print("✅ Deep-translator library loaded successfully")
    except ImportError as e:
        print(f"⚠️ Deep-translator not available: {e}")
        
        # Try googletrans as fallback
        try:
            import googletrans
            TRANSLATION_AVAILABLE = True
            USING_DEEP_TRANSLATOR = False
            googletrans_translator = googletrans.Translator()
            print("✅ Googletrans library loaded successfully")
        except ImportError as googletrans_error:
            print(f"⚠️ Googletrans not available: {googletrans_error}")
            print("   Install deep-translator: pip install deep-translator")
            TRANSLATION_AVAILABLE = False
            googletrans_translator = None
            
except ImportError as e:
    print(f"⚠️ Language detection not available: {e}")
    print("   Install with: pip install langdetect deep-translator")
    TRANSLATION_AVAILABLE = False
    googletrans_translator = None

print(f"🌐 Translation Status: Available={TRANSLATION_AVAILABLE}, Using Deep Translator={USING_DEEP_TRANSLATOR}")

app = Flask(__name__)
app.secret_key = 'audiobook_secret_key_2024'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'sample_docs'
app.config['AUDIO_FOLDER'] = 'audio_output'
app.config['VOICE_SAMPLES_FOLDER'] = 'voice_samples'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Simple user storage (use database in production)
users_db = {
    'admin': {
        'password_hash': generate_password_hash('admin123'),
        'role': 'author',
        'voice_samples': []
    }
}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
os.makedirs(app.config['VOICE_SAMPLES_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
os.makedirs(app.config['VOICE_SAMPLES_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def analyze_text_emotion(text):
    """Analyze text for emotional content to adjust voice parameters"""
    emotion_keywords = {
        'excitement': ['excited', 'amazing', 'wonderful', 'fantastic', 'incredible', '!'],
        'sadness': ['sad', 'tragic', 'sorrow', 'grief', 'melancholy', 'tears'],
        'anger': ['angry', 'furious', 'rage', 'mad', 'annoyed', 'irritated'],
        'fear': ['scared', 'frightened', 'terrified', 'afraid', 'panic', 'horror'],
        'joy': ['happy', 'joyful', 'cheerful', 'delighted', 'pleased', 'glad'],
        'mystery': ['mysterious', 'strange', 'eerie', 'unknown', 'secret', 'hidden'],
        'romance': ['love', 'romantic', 'heart', 'kiss', 'tender', 'affection'],
        'action': ['fight', 'battle', 'run', 'chase', 'quick', 'fast', 'suddenly']
    }
    
    text_lower = text.lower()
    emotion_scores = {}
    
    for emotion, keywords in emotion_keywords.items():
        score = sum(text_lower.count(keyword) for keyword in keywords)
        emotion_scores[emotion] = score
    
    # Determine dominant emotion
    max_score = max(emotion_scores.values()) if emotion_scores.values() else 0
    dominant_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k]) if max_score > 0 else 'neutral'
    intensity = min(max_score / 10, 1.0)  # Normalize to 0-1
    
    return dominant_emotion, intensity

def get_natural_voice_settings(emotion, intensity, base_rate=175, base_volume=0.9):
    """Generate natural voice settings based on emotion and intensity"""
    settings = {
        'rate': base_rate,
        'volume': base_volume,
        'pitch_variation': 0,
        'pause_multiplier': 1.0
    }
    
    # More dramatic emotion-based adjustments for natural speech
    emotion_adjustments = {
        'excitement': {'rate': 35, 'volume': 0.15, 'pitch_variation': 20, 'pause_multiplier': 0.6},
        'sadness': {'rate': -45, 'volume': -0.15, 'pitch_variation': -15, 'pause_multiplier': 1.8},
        'anger': {'rate': 25, 'volume': 0.15, 'pitch_variation': 15, 'pause_multiplier': 0.5},
        'fear': {'rate': 40, 'volume': -0.1, 'pitch_variation': 25, 'pause_multiplier': 0.7},
        'joy': {'rate': 20, 'volume': 0.1, 'pitch_variation': 18, 'pause_multiplier': 0.8},
        'mystery': {'rate': -25, 'volume': -0.1, 'pitch_variation': -8, 'pause_multiplier': 1.6},
        'romance': {'rate': -15, 'volume': 0.05, 'pitch_variation': 8, 'pause_multiplier': 1.4},
        'action': {'rate': 45, 'volume': 0.2, 'pitch_variation': 20, 'pause_multiplier': 0.4}
    }
    
    if emotion in emotion_adjustments:
        adjustments = emotion_adjustments[emotion]
        # Apply stronger intensity effects
        multiplier = max(intensity, 0.3)  # Minimum 0.3 for noticeable effect
        settings['rate'] += int(adjustments['rate'] * multiplier)
        settings['volume'] += adjustments['volume'] * multiplier
        settings['pitch_variation'] = adjustments['pitch_variation'] * multiplier
        settings['pause_multiplier'] = 1.0 + (adjustments['pause_multiplier'] - 1.0) * multiplier
    
    # Ensure values stay within reasonable bounds but allow more variation
    settings['rate'] = max(80, min(280, settings['rate']))  # Wider range
    settings['volume'] = max(0.1, min(1.0, settings['volume']))
    
    return settings

def enhance_text_naturalness(text, emotion='neutral', intensity=0.5, continuous_flow=True):
    """Advanced text enhancement for natural speech with emotion-based adjustments and continuous flow"""
    if continuous_flow:
        # For continuous flow, minimize pauses and create smooth transitions
        text = create_continuous_flow(text, emotion, intensity)
    else:
        # Original approach with pauses
        text = create_traditional_flow(text, emotion, intensity)
    
    return text

def create_continuous_flow(text, emotion='neutral', intensity=0.5):
    """Create smooth, continuous speech flow without formal breaks - Enhanced for natural speech"""
    # More aggressive removal of robotic patterns
    text = re.sub(r'([.!?])\s*([.!?])+', r'\1 ', text)
    text = re.sub(r'\s+', ' ', text)  # Clean up spaces first
    
    # Replace formal language with natural speech patterns
    natural_replacements = {
        r'\bhowever\b': 'but',
        r'\btherefore\b': 'so',
        r'\bnevertheless\b': 'but still',
        r'\bfurthermore\b': 'and also',
        r'\bmoreover\b': 'plus',
        r'\bin addition\b': 'also',
        r'\bconsequently\b': 'so then',
        r'\bsubsequently\b': 'then',
        r'\badditionally\b': 'and',
        r'\baccordingly\b': 'so',
        r'\bthus\b': 'so',
        r'\bhence\b': 'so',
        r'\bwhereby\b': 'where',
        r'\bwhereas\b': 'while',
        r'\bunfortunately\b': 'sadly',
        r'\bfortunately\b': 'luckily',
        r'\bobviously\b': 'clearly',
        r'\bcertainly\b': 'definitely',
        r'\bundoubtedly\b': 'for sure',
        r'\bperhaps\b': 'maybe',
        r'\bpossibly\b': 'maybe',
        r'\bprobably\b': 'likely',
        r'\bessentiatly\b': 'basically',
        r'\bfundamentally\b': 'basically',
        r'\bultimately\b': 'in the end',
        r'\binitially\b': 'at first',
        r'\boriginally\b': 'at first',
        r'\bspecifically\b': 'especially',
        r'\bparticularly\b': 'especially'
    }
    
    for formal, casual in natural_replacements.items():
        text = re.sub(formal, casual, text, flags=re.IGNORECASE)
    
    # Make contractions more natural
    contractions = {
        r'\bit is\b': "it's",
        r'\bthey are\b': "they're", 
        r'\byou are\b': "you're",
        r'\bwe are\b': "we're",
        r'\bI am\b': "I'm",
        r'\bhe is\b': "he's",
        r'\bshe is\b': "she's",
        r'\bwho is\b': "who's",
        r'\bwhat is\b': "what's",
        r'\bthere is\b': "there's",
        r'\bdo not\b': "don't",
        r'\bdoes not\b': "doesn't",
        r'\bdid not\b': "didn't",
        r'\bwill not\b': "won't",
        r'\bwould not\b': "wouldn't",
        r'\bcould not\b': "couldn't",
        r'\bshould not\b': "shouldn't",
        r'\bcannot\b': "can't",
        r'\bis not\b': "isn't",
        r'\bare not\b': "aren't",
        r'\bwas not\b': "wasn't",
        r'\bwere not\b': "weren't",
        r'\bhave not\b': "haven't",
        r'\bhas not\b': "hasn't",
        r'\bhad not\b': "hadn't"
    }
    
    for long_form, contraction in contractions.items():
        text = re.sub(long_form, contraction, text, flags=re.IGNORECASE)
    
    # Emotion-based flow adjustments with more natural patterns
    if emotion == 'excitement':
        # Fast, energetic flow - remove most pauses
        text = re.sub(r'([.!?])\s+', r'\1 ', text)
        text = re.sub(r'([,])\s+', r'\1 ', text)
        text = add_excitement_flow(text)
        # Add natural speech fillers for excitement
        text = re.sub(r'\b(amazing|incredible|fantastic|wonderful)\b', r'oh wow, \1', text, flags=re.IGNORECASE)
        
    elif emotion == 'sadness':
        # Slower, more reflective with gentle pauses
        text = re.sub(r'([.])\s+', r'\1... ', text)
        text = add_melancholic_flow(text)
        # Add reflective pauses
        text = re.sub(r'\b(remember|think|feel|sad)\b', r'... \1', text, flags=re.IGNORECASE)
        
    elif emotion == 'mystery':
        # Intriguing, suspenseful flow
        text = add_mysterious_flow(text)
        text = re.sub(r'\b(dark|hidden|secret|strange)\b', r'... \1 ...', text, flags=re.IGNORECASE)
        
    elif emotion == 'romance':
        # Gentle, warm flow with soft pauses
        text = add_romantic_flow(text)
        text = re.sub(r'\b(love|heart|beautiful|tender)\b', r'... \1', text, flags=re.IGNORECASE)
        
    elif emotion == 'action':
        # Quick, dynamic flow - minimal pauses
        text = add_action_flow(text)
        text = re.sub(r'\b(suddenly|quickly|fast|ran|jumped)\b', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'([.!?])\s+', r'\1 ', text)  # Remove pauses for action
        
    else:
        # Natural conversational flow
        text = add_conversational_flow(text)
        # Add natural speech patterns
        sentences = text.split('.')
        enhanced_sentences = []
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Occasionally add natural connectors
                if i > 0 and len(sentence.strip()) > 20 and i % 5 == 0:
                    connectors = ['you know', 'I mean', 'well', 'so', 'and', 'now']
                    connector = connectors[i % len(connectors)]
                    sentence = f" {connector}, {sentence.strip()}"
                enhanced_sentences.append(sentence.strip())
        text = '. '.join(enhanced_sentences)
    
    # Final cleanup - remove excessive punctuation that causes robotic pauses
    text = re.sub(r'\.{3,}', '...', text)  # Limit ellipses
    text = re.sub(r'\s+', ' ', text)  # Clean up spaces
    text = re.sub(r'([,;:])\s*([,;:])', r'\1', text)  # Remove double punctuation
    
    return text.strip()

def add_excitement_flow(text):
    """Add energetic, enthusiastic flow patterns"""
    # Quick transitions
    text = re.sub(r'\b(amazing|incredible|fantastic|wonderful)\b', r'\1!', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(and then)\b', 'and boom', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(very)\s+(\w+)', r'super \2', text, flags=re.IGNORECASE)
    return text

def add_melancholic_flow(text):
    """Add gentle, reflective flow patterns"""
    # Softer transitions
    text = re.sub(r'\b(said)\b', 'whispered', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(went)\b', 'drifted', text, flags=re.IGNORECASE)
    return text

def add_mysterious_flow(text):
    """Add suspenseful, intriguing flow patterns"""
    text = re.sub(r'\b(suddenly)\b', 'out of nowhere', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(appeared)\b', 'emerged from the shadows', text, flags=re.IGNORECASE)
    return text

def add_romantic_flow(text):
    """Add warm, tender flow patterns"""
    text = re.sub(r'\b(looked at)\b', 'gazed into', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(touched)\b', 'caressed', text, flags=re.IGNORECASE)
    return text

def add_action_flow(text):
    """Add dynamic, fast-paced flow patterns"""
    text = re.sub(r'\b(ran)\b', 'sprinted', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(jumped)\b', 'leaped', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(quickly)\b', 'in a flash', text, flags=re.IGNORECASE)
    return text

def add_conversational_flow(text):
    """Add natural, conversational flow patterns"""
    # Make it sound more like natural speech
    text = re.sub(r'\b(it is)\b', "it's", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(they are)\b', "they're", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(you are)\b', "you're", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(we are)\b', "we're", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(I am)\b', "I'm", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(do not)\b', "don't", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(will not)\b', "won't", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(cannot)\b', "can't", text, flags=re.IGNORECASE)
    
    # Add natural speech fillers occasionally
    sentences = text.split('.')
    enhanced_sentences = []
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            # Occasionally add natural connectors
            if i > 0 and len(sentence.strip()) > 20:
                connectors = ['you know', 'I mean', 'well', 'so']
                if i % 4 == 0:  # Every 4th sentence
                    connector = connectors[i % len(connectors)]
                    sentence = f"{connector}, {sentence.strip()}"
            enhanced_sentences.append(sentence.strip())
    
    return '. '.join(enhanced_sentences)

def create_traditional_flow(text, emotion='neutral', intensity=0.5):
    """Original approach with pauses for formal speech"""
    # Base sentence processing
    sentences = re.split(r'[.!?]+', text)
    enhanced_sentences = []
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        sentence = sentence.strip()
        
        # Add natural breathing pauses
        if len(sentence) > 100:
            # Insert pauses at natural break points
            sentence = re.sub(r'\b(and|but|or|so|yet|for|nor|because|since|although|while|when|where|if|unless)\s+', 
                            r'\1... ', sentence)
        
        # Emotion-based enhancements
        if emotion == 'excitement':
            sentence = re.sub(r'\b(amazing|wonderful|incredible)\b', r'\1!', sentence, flags=re.IGNORECASE)
            sentence = re.sub(r'([!]+)', r'\1... ', sentence)
        elif emotion == 'sadness':
            sentence = re.sub(r'([.,])\s+', r'\1.... ', sentence)
        elif emotion == 'mystery':
            sentence = re.sub(r'\b(mysterious|strange|unknown)\b', r'..... \1', sentence, flags=re.IGNORECASE)
        elif emotion == 'action':
            sentence = re.sub(r'\b(suddenly|quickly|fast)\b', r'\1!', sentence, flags=re.IGNORECASE)
        elif emotion == 'romance':
            sentence = re.sub(r'\b(love|heart|tender)\b', r'... \1 ...', sentence, flags=re.IGNORECASE)
        
        # Add emphasis markers for important words
        sentence = re.sub(r'\b(very|really|extremely|absolutely)\s+(\w+)', r'\1... \2', sentence, flags=re.IGNORECASE)
        
        # Natural dialogue enhancements
        sentence = re.sub(r'"([^"]+)"', r'... "\1" ...', sentence)
        
        enhanced_sentences.append(sentence)
    
    # Join with appropriate pauses based on emotion
    pause_marker = '.... ' if intensity > 0.7 else '... ' if intensity > 0.3 else '. '
    result = pause_marker.join(enhanced_sentences)
    
    # Add final period if missing
    if not result.endswith(('.', '!', '?')):
        result += '.'
    
    return result

# AI Storytelling and Analysis Functions
def analyze_story_content(text):
    """Analyze story content for themes, characters, and narrative elements"""
    analysis = {
        'word_count': len(text.split()),
        'sentence_count': len(re.findall(r'[.!?]+', text)),
        'themes': [],
        'characters': [],
        'narrative_elements': [],
        'reading_level': 'intermediate',
        'genre_hints': []
    }
    
    text_lower = text.lower()
    
    # Theme detection
    theme_keywords = {
        'adventure': ['adventure', 'journey', 'quest', 'explore', 'travel', 'discover'],
        'romance': ['love', 'heart', 'romance', 'kiss', 'relationship', 'wedding'],
        'mystery': ['mystery', 'detective', 'clue', 'secret', 'hidden', 'investigate'],
        'fantasy': ['magic', 'wizard', 'dragon', 'fairy', 'enchanted', 'spell'],
        'science_fiction': ['space', 'robot', 'future', 'technology', 'alien', 'time'],
        'horror': ['scary', 'ghost', 'haunted', 'fear', 'dark', 'nightmare'],
        'family': ['family', 'mother', 'father', 'children', 'home', 'parent']
    }
    
    for theme, keywords in theme_keywords.items():
        score = sum(text_lower.count(keyword) for keyword in keywords)
        if score > 0:
            analysis['themes'].append({'theme': theme, 'strength': min(score, 10)})
    
    # Character name detection (simple heuristic)
    sentences = re.split(r'[.!?]+', text)
    potential_names = set()
    for sentence in sentences:
        words = sentence.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2 and word.isalpha():
                if word.lower() not in ['i', 'the', 'and', 'but', 'or', 'so', 'yet', 'for', 'nor', 'a', 'an']:
                    potential_names.add(word)
    
    analysis['characters'] = list(potential_names)[:10]  # Limit to 10 potential characters
    
    # Narrative elements
    narrative_patterns = {
        'dialogue': len(re.findall(r'"[^"]+"', text)),
        'descriptive_passages': len(re.findall(r'\b(beautiful|magnificent|terrifying|mysterious|ancient)\b', text, re.IGNORECASE)),
        'action_sequences': len(re.findall(r'\b(ran|jumped|fought|screamed|rushed|suddenly)\b', text, re.IGNORECASE)),
        'emotional_moments': len(re.findall(r'\b(tears|joy|anger|fear|love|hate)\b', text, re.IGNORECASE))
    }
    
    analysis['narrative_elements'] = narrative_patterns
    
    return analysis

def generate_story_questions(text):
    """Generate comprehension and discussion questions based on story content"""
    analysis = analyze_story_content(text)
    questions = []
    
    # Basic comprehension questions
    if analysis['characters']:
        main_characters = analysis['characters'][:3]
        questions.append(f"Who are the main characters in this story? (Hint: {', '.join(main_characters)})")
        for char in main_characters[:2]:
            questions.append(f"What role does {char} play in the story?")
    
    # Theme-based questions
    if analysis['themes']:
        main_theme = analysis['themes'][0]['theme']
        theme_questions = {
            'adventure': "What challenges do the characters face during their adventure?",
            'romance': "How do the romantic relationships develop in the story?",
            'mystery': "What clues help solve the mystery in the story?",
            'fantasy': "What magical elements make this story fantastical?",
            'family': "How do family relationships affect the characters?"
        }
        if main_theme in theme_questions:
            questions.append(theme_questions[main_theme])
    
    # Narrative structure questions
    questions.extend([
        "What is the main conflict or problem in the story?",
        "How is the conflict resolved?",
        "What is the setting of the story?",
        "What emotions did this story make you feel?",
        "What lesson or message does the story convey?"
    ])
    
    # Critical thinking questions
    questions.extend([
        "How would you change the ending of this story?",
        "Which character do you relate to most and why?",
        "What would happen if the story continued for another chapter?"
    ])
    
    return questions[:8]  # Return up to 8 questions

def provide_story_insights(text, question):
    """Provide AI-generated insights and answers about the story"""
    analysis = analyze_story_content(text)
    question_lower = question.lower()
    
    # Simple keyword-based response generation
    if 'character' in question_lower:
        if analysis['characters']:
            return f"The main characters appear to be: {', '.join(analysis['characters'][:5])}. Each character contributes to the story's development through their actions and relationships."
        else:
            return "The story focuses more on events and themes rather than specific named characters."
    
    elif 'theme' in question_lower or 'message' in question_lower:
        if analysis['themes']:
            themes = [t['theme'].replace('_', ' ') for t in analysis['themes'][:3]]
            return f"The main themes in this story include: {', '.join(themes)}. These themes are woven throughout the narrative to create deeper meaning."
        else:
            return "The story explores universal human experiences and emotions that readers can relate to."
    
    elif 'conflict' in question_lower or 'problem' in question_lower:
        return "The central conflict drives the narrative forward and creates tension that keeps readers engaged. Look for moments where characters face challenges or make difficult decisions."
    
    elif 'setting' in question_lower:
        return "The setting provides the backdrop for the story's events. Pay attention to descriptions of time, place, and atmosphere that help create the story's mood."
    
    elif 'emotion' in question_lower or 'feel' in question_lower:
        emotions = analyze_text_emotion(text)
        return f"This story evokes {emotions[0]} emotions with an intensity of {emotions[1]:.1f}/1.0. The emotional journey helps readers connect with the characters and their experiences."
    
    else:
        return "That's an excellent question! Consider how the story elements work together - characters, setting, plot, and theme all contribute to the overall narrative. What patterns or connections do you notice?"

# Authentication Functions
def is_authenticated():
    """Check if user is logged in"""
    return 'user_id' in session

def is_author():
    """Check if current user is an author"""
    if not is_authenticated():
        return False
    user_id = session['user_id']
    return user_id in users_db and users_db[user_id].get('role') == 'author'

def authenticate_user(username, password):
    """Authenticate user credentials"""
    if username in users_db:
        if check_password_hash(users_db[username]['password_hash'], password):
            return users_db[username]
    return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Expanded voice packs with diverse personalities and continuous flow settings
VOICE_PACKS = {
    # Classic voices
    'female_warm': {
        'keywords': ['zira', 'hazel', 'susan', 'female', 'woman', 'cortana', 'eva'],
        'avoid': ['male', 'man', 'david', 'mark'],
        'personality': 'warm_caring',
        'flow_style': 'conversational',
        'description': 'Warm, caring narrator perfect for emotional stories and novels'
    },
    'male_deep': {
        'keywords': ['david', 'mark', 'male', 'man', 'deep', 'bass'],
        'avoid': ['female', 'woman', 'high', 'soprano'],
        'personality': 'authoritative',
        'flow_style': 'dramatic',
        'description': 'Rich, deep voice perfect for dramatic narratives and thrillers'
    },
    
    # Personality-based voice packs
    'cheerful_energetic': {
        'keywords': ['zira', 'hazel', 'female', 'young', 'bright'],
        'avoid': ['male', 'man', 'monotone'],
        'personality': 'upbeat',
        'flow_style': 'energetic',
        'description': 'Bubbly, energetic voice that brings joy and excitement to any story'
    },
    'calm_meditative': {
        'keywords': ['susan', 'peaceful', 'calm', 'meditation'],
        'avoid': ['loud', 'harsh', 'aggressive'],
        'personality': 'zen',  
        'flow_style': 'flowing',
        'description': 'Peaceful, meditative voice perfect for relaxation and mindfulness content'
    },
    'adventurous_explorer': {
        'keywords': ['adventure', 'explorer', 'dynamic', 'travel'],
        'avoid': ['boring', 'monotone'],
        'personality': 'adventurous',
        'flow_style': 'dynamic',
        'description': 'Dynamic voice that captures the spirit of adventure and exploration'
    },
    'mysterious_storyteller': {
        'keywords': ['mystery', 'dark', 'enigmatic', 'storyteller'],
        'avoid': ['bright', 'cheerful'],
        'personality': 'mysterious',
        'flow_style': 'suspenseful',
        'description': 'Enigmatic voice perfect for mysteries, thrillers, and dark tales'
    },
    'romantic_dreamer': {
        'keywords': ['romantic', 'dreamy', 'soft', 'tender'],
        'avoid': ['harsh', 'aggressive'],
        'personality': 'romantic',
        'flow_style': 'gentle',
        'description': 'Soft, dreamy voice that brings romance and emotion to life'
    },
    'wise_mentor': {
        'keywords': ['wise', 'mentor', 'teacher', 'elder'],
        'avoid': ['young', 'inexperienced'],
        'personality': 'wise',
        'flow_style': 'thoughtful',
        'description': 'Wise, experienced voice perfect for educational content and life lessons'
    },
    'playful_comedian': {
        'keywords': ['funny', 'playful', 'comedy', 'humorous'],
        'avoid': ['serious', 'formal'],
        'personality': 'humorous',
        'flow_style': 'playful',
        'description': 'Playful, humorous voice that adds fun and laughter to stories'
    },
    'confident_leader': {
        'keywords': ['confident', 'leader', 'strong', 'powerful'],
        'avoid': ['weak', 'uncertain'],
        'personality': 'confident',
        'flow_style': 'authoritative',
        'description': 'Strong, confident voice perfect for leadership content and motivational stories'
    },
    'gentle_healer': {
        'keywords': ['gentle', 'healing', 'therapeutic', 'soothing'],
        'avoid': ['harsh', 'aggressive'],
        'personality': 'healing',
        'flow_style': 'soothing',
        'description': 'Gentle, therapeutic voice perfect for healing and wellness content'
    },
    'curious_scientist': {
        'keywords': ['curious', 'scientific', 'analytical', 'research'],
        'avoid': ['emotional', 'dramatic'],
        'personality': 'analytical',
        'flow_style': 'informative',
        'description': 'Curious, analytical voice perfect for educational and scientific content'
    },
    'passionate_artist': {
        'keywords': ['passionate', 'artistic', 'creative', 'expressive'],
        'avoid': ['bland', 'monotone'],
        'personality': 'artistic',
        'flow_style': 'expressive',
        'description': 'Passionate, expressive voice that brings creativity and artistry to life'
    },
    'street_smart': {
        'keywords': ['street', 'urban', 'modern', 'cool'],
        'avoid': ['formal', 'academic'],
        'personality': 'street_smart',
        'flow_style': 'casual',
        'description': 'Cool, street-smart voice perfect for urban stories and contemporary fiction'
    },
    'nature_lover': {
        'keywords': ['nature', 'outdoor', 'earth', 'green'],
        'avoid': ['artificial', 'synthetic'],
        'personality': 'earthy',
        'flow_style': 'natural',
        'description': 'Earthy, natural voice that connects with nature and environmental themes'
    },
    'tech_enthusiast': {
        'keywords': ['tech', 'digital', 'modern', 'innovation'],
        'avoid': ['old-fashioned', 'traditional'],
        'personality': 'innovative',
        'flow_style': 'modern',
        'description': 'Modern, tech-savvy voice perfect for science fiction and technology content'
    },
    'spiritual_guide': {
        'keywords': ['spiritual', 'guide', 'enlightened', 'transcendent'],
        'avoid': ['materialistic', 'shallow'],
        'personality': 'spiritual',
        'flow_style': 'transcendent',
        'description': 'Spiritual, enlightened voice perfect for philosophical and spiritual content'
    },
    'rebel_activist': {
        'keywords': ['rebel', 'activist', 'revolutionary', 'change'],
        'avoid': ['conformist', 'traditional'],
        'personality': 'rebellious',
        'flow_style': 'passionate',
        'description': 'Bold, rebellious voice that challenges the status quo and inspires change'
    },
    'dreamy_poet': {
        'keywords': ['dreamy', 'poetic', 'lyrical', 'artistic'],
        'avoid': ['practical', 'mundane'],
        'personality': 'poetic',
        'flow_style': 'lyrical',
        'description': 'Dreamy, poetic voice that brings beauty and lyricism to any content'
    },
    'friendly_neighbor': {
        'keywords': ['friendly', 'neighborly', 'warm', 'approachable'],
        'avoid': ['cold', 'distant'],
        'personality': 'neighborly',
        'flow_style': 'friendly',
        'description': 'Warm, friendly voice like talking to your favorite neighbor over coffee'
    },
    'cosmic_explorer': {
        'keywords': ['cosmic', 'space', 'universe', 'infinite'],
        'avoid': ['earthbound', 'limited'],
        'personality': 'cosmic',
        'flow_style': 'expansive',
        'description': 'Expansive, cosmic voice perfect for science fiction and space adventures'
    }
}

def extract_text_from_file(filepath):
    """Extract text from various file formats"""
    text = ""
    file_ext = filepath.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
        
        elif file_ext == 'pdf':
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        
        elif file_ext == 'docx':
            doc = docx.Document(filepath)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
    
    except Exception as e:
        print(f"Error extracting text from {filepath}: {str(e)}")
        return None
    
    return text.strip()

# Note: Translator initialization is handled above in the import section

# Supported languages with voice optimization (80+ languages)
SUPPORTED_LANGUAGES = {
    # Major European Languages
    'en': {'name': 'English', 'flag': '🇺🇸', 'voice_keywords': ['english', 'david', 'zira', 'mark', 'hazel']},
    'es': {'name': 'Spanish', 'flag': '🇪🇸', 'voice_keywords': ['spanish', 'español', 'sabina', 'helena']},
    'fr': {'name': 'French', 'flag': '🇫🇷', 'voice_keywords': ['french', 'français', 'hortense', 'paul']},
    'de': {'name': 'German', 'flag': '🇩🇪', 'voice_keywords': ['german', 'deutsch', 'hedda', 'stefan']},
    'it': {'name': 'Italian', 'flag': '🇮🇹', 'voice_keywords': ['italian', 'italiano', 'elsa', 'cosimo']},
    'pt': {'name': 'Portuguese', 'flag': '🇵🇹', 'voice_keywords': ['portuguese', 'português', 'helia', 'daniel']},
    'ru': {'name': 'Russian', 'flag': '🇷🇺', 'voice_keywords': ['russian', 'русский', 'irina', 'pavel']},
    'nl': {'name': 'Dutch', 'flag': '🇳🇱', 'voice_keywords': ['dutch', 'nederlands', 'frank']},
    'sv': {'name': 'Swedish', 'flag': '🇸🇪', 'voice_keywords': ['swedish', 'svenska', 'bengt']},
    'no': {'name': 'Norwegian', 'flag': '🇳🇴', 'voice_keywords': ['norwegian', 'norsk', 'jon']},
    'da': {'name': 'Danish', 'flag': '🇩🇰', 'voice_keywords': ['danish', 'dansk', 'helle']},
    'fi': {'name': 'Finnish', 'flag': '🇫🇮', 'voice_keywords': ['finnish', 'suomi', 'heidi']},
    'pl': {'name': 'Polish', 'flag': '🇵🇱', 'voice_keywords': ['polish', 'polski', 'paulina']},
    'cs': {'name': 'Czech', 'flag': '🇨🇿', 'voice_keywords': ['czech', 'čeština', 'jakub']},
    'sk': {'name': 'Slovak', 'flag': '🇸🇰', 'voice_keywords': ['slovak', 'slovenčina', 'filip']},
    'hu': {'name': 'Hungarian', 'flag': '🇭🇺', 'voice_keywords': ['hungarian', 'magyar', 'szabolcs']},
    'ro': {'name': 'Romanian', 'flag': '🇷🇴', 'voice_keywords': ['romanian', 'română', 'andrei']},
    'bg': {'name': 'Bulgarian', 'flag': '🇧🇬', 'voice_keywords': ['bulgarian', 'български', 'ivan']},
    'hr': {'name': 'Croatian', 'flag': '🇭🇷', 'voice_keywords': ['croatian', 'hrvatski', 'matej']},
    'sr': {'name': 'Serbian', 'flag': '🇷🇸', 'voice_keywords': ['serbian', 'српски', 'stefan']},
    'sl': {'name': 'Slovenian', 'flag': '🇸🇮', 'voice_keywords': ['slovenian', 'slovenščina', 'lado']},
    'et': {'name': 'Estonian', 'flag': '🇪🇪', 'voice_keywords': ['estonian', 'eesti', 'kert']},
    'lv': {'name': 'Latvian', 'flag': '🇱🇻', 'voice_keywords': ['latvian', 'latviešu', 'nils']},
    'lt': {'name': 'Lithuanian', 'flag': '🇱🇹', 'voice_keywords': ['lithuanian', 'lietuvių', 'leonas']},
    'el': {'name': 'Greek', 'flag': '🇬🇷', 'voice_keywords': ['greek', 'ελληνικά', 'stefanos']},
    'tr': {'name': 'Turkish', 'flag': '🇹🇷', 'voice_keywords': ['turkish', 'türkçe', 'tolga']},
    'uk': {'name': 'Ukrainian', 'flag': '🇺🇦', 'voice_keywords': ['ukrainian', 'українська', 'ostap']},
    'be': {'name': 'Belarusian', 'flag': '🇧🇾', 'voice_keywords': ['belarusian', 'беларуская', 'uladzimir']},
    'mk': {'name': 'Macedonian', 'flag': '🇲🇰', 'voice_keywords': ['macedonian', 'македонски', 'aleksandar']},
    'mt': {'name': 'Maltese', 'flag': '🇲🇹', 'voice_keywords': ['maltese', 'malti', 'ġorġ']},
    'is': {'name': 'Icelandic', 'flag': '🇮🇸', 'voice_keywords': ['icelandic', 'íslenska', 'karl']},
    'ga': {'name': 'Irish', 'flag': '🇮🇪', 'voice_keywords': ['irish', 'gaeilge', 'colm']},
    'cy': {'name': 'Welsh', 'flag': '🏴󠁧󠁢󠁷󠁬󠁳󠁿', 'voice_keywords': ['welsh', 'cymraeg', 'geraint']},
    'eu': {'name': 'Basque', 'flag': '🇪🇸', 'voice_keywords': ['basque', 'euskera', 'mikel']},
    'ca': {'name': 'Catalan', 'flag': '🇪🇸', 'voice_keywords': ['catalan', 'català', 'jordi']},
    'gl': {'name': 'Galician', 'flag': '🇪🇸', 'voice_keywords': ['galician', 'galego', 'roi']},
    
    # Asian Languages
    'zh': {'name': 'Chinese (Simplified)', 'flag': '🇨🇳', 'voice_keywords': ['chinese', '中文', 'huihui', 'kangkang']},
    'zh-tw': {'name': 'Chinese (Traditional)', 'flag': '🇹🇼', 'voice_keywords': ['chinese', '繁體中文', 'hanhan', 'zhiwei']},
    'ja': {'name': 'Japanese', 'flag': '🇯🇵', 'voice_keywords': ['japanese', '日本語', 'ayumi', 'ichiro']},
    'ko': {'name': 'Korean', 'flag': '🇰🇷', 'voice_keywords': ['korean', '한국어', 'heami']},
    'th': {'name': 'Thai', 'flag': '🇹🇭', 'voice_keywords': ['thai', 'ไทย', 'pattara']},
    'vi': {'name': 'Vietnamese', 'flag': '🇻🇳', 'voice_keywords': ['vietnamese', 'tiếng việt', 'an']},
    'id': {'name': 'Indonesian', 'flag': '🇮🇩', 'voice_keywords': ['indonesian', 'bahasa indonesia', 'andika']},
    'ms': {'name': 'Malay', 'flag': '🇲🇾', 'voice_keywords': ['malay', 'bahasa melayu', 'rizwan']},
    'tl': {'name': 'Filipino', 'flag': '🇵🇭', 'voice_keywords': ['filipino', 'tagalog', 'rosa']},
    'my': {'name': 'Myanmar (Burmese)', 'flag': '🇲🇲', 'voice_keywords': ['myanmar', 'burmese', 'မြန်မာ']},
    'km': {'name': 'Khmer', 'flag': '🇰🇭', 'voice_keywords': ['khmer', 'ខ្មែរ', 'pisach']},
    'lo': {'name': 'Lao', 'flag': '🇱🇦', 'voice_keywords': ['lao', 'ລາວ', 'keomany']},
    'mn': {'name': 'Mongolian', 'flag': '🇲🇳', 'voice_keywords': ['mongolian', 'モンゴル', 'batbayar']},
    'ne': {'name': 'Nepali', 'flag': '🇳🇵', 'voice_keywords': ['nepali', 'नेपाली', 'hemkala']},
    'si': {'name': 'Sinhala', 'flag': '🇱🇰', 'voice_keywords': ['sinhala', 'සිංහල', 'sihan']},
    'bn': {'name': 'Bengali', 'flag': '🇧🇩', 'voice_keywords': ['bengali', 'বাংলা', 'bashkar']},
    
    # Indian Subcontinent Languages
    'hi': {'name': 'Hindi', 'flag': '🇮🇳', 'voice_keywords': ['hindi', 'हिन्दी', 'kalpana']},
    'ta': {'name': 'Tamil', 'flag': '🇮🇳', 'voice_keywords': ['tamil', 'தமிழ்', 'valluvar']},
    'te': {'name': 'Telugu', 'flag': '🇮🇳', 'voice_keywords': ['telugu', 'తెలుగు', 'chitra']},
    'kn': {'name': 'Kannada', 'flag': '🇮🇳', 'voice_keywords': ['kannada', 'ಕನ್ನಡ', 'pattayya']},
    'ml': {'name': 'Malayalam', 'flag': '🇮🇳', 'voice_keywords': ['malayalam', 'മലയാളം', 'midhun']},
    'mr': {'name': 'Marathi', 'flag': '🇮🇳', 'voice_keywords': ['marathi', 'मराठी', 'manohar']},
    'gu': {'name': 'Gujarati', 'flag': '🇮🇳', 'voice_keywords': ['gujarati', 'ગુજરાતી', 'dhwani']},
    'pa': {'name': 'Punjabi', 'flag': '🇮🇳', 'voice_keywords': ['punjabi', 'ਪੰਜਾਬੀ', 'ajit']},
    'or': {'name': 'Odia', 'flag': '🇮🇳', 'voice_keywords': ['odia', 'ଓଡ଼ିଆ', 'subhasree']},
    'as': {'name': 'Assamese', 'flag': '🇮🇳', 'voice_keywords': ['assamese', 'অসমীয়া', 'priyanka']},
    'ur': {'name': 'Urdu', 'flag': '🇵🇰', 'voice_keywords': ['urdu', 'اردو', 'salman']},
    'sd': {'name': 'Sindhi', 'flag': '🇵🇰', 'voice_keywords': ['sindhi', 'سنڌي', 'amjad']},
    'ps': {'name': 'Pashto', 'flag': '🇦🇫', 'voice_keywords': ['pashto', 'پښتو', 'gul']},
    'fa': {'name': 'Persian', 'flag': '🇮🇷', 'voice_keywords': ['persian', 'فارسی', 'hedayat']},
    
    # Middle Eastern & African Languages
    'ar': {'name': 'Arabic', 'flag': '🇸🇦', 'voice_keywords': ['arabic', 'عربي', 'naayf']},
    'he': {'name': 'Hebrew', 'flag': '🇮🇱', 'voice_keywords': ['hebrew', 'עברית', 'asaf']},
    'am': {'name': 'Amharic', 'flag': '🇪🇹', 'voice_keywords': ['amharic', 'አማርኛ', 'meron']},
    'ti': {'name': 'Tigrinya', 'flag': '🇪🇷', 'voice_keywords': ['tigrinya', 'ትግርኛ', 'haben']},
    'om': {'name': 'Oromo', 'flag': '🇪🇹', 'voice_keywords': ['oromo', 'afaan oromoo', 'tolesa']},
    'so': {'name': 'Somali', 'flag': '🇸🇴', 'voice_keywords': ['somali', 'soomaali', 'amina']},
    'sw': {'name': 'Swahili', 'flag': '🇰🇪', 'voice_keywords': ['swahili', 'kiswahili', 'salama']},
    'zu': {'name': 'Zulu', 'flag': '🇿🇦', 'voice_keywords': ['zulu', 'isizulu', 'lindiwe']},
    'xh': {'name': 'Xhosa', 'flag': '🇿🇦', 'voice_keywords': ['xhosa', 'isixhosa', 'nomsa']},
    'af': {'name': 'Afrikaans', 'flag': '🇿🇦', 'voice_keywords': ['afrikaans', 'afrikaans', 'willem']},
    'ig': {'name': 'Igbo', 'flag': '🇳🇬', 'voice_keywords': ['igbo', 'asụsụ igbo', 'adaeze']},
    'yo': {'name': 'Yoruba', 'flag': '🇳🇬', 'voice_keywords': ['yoruba', 'èdè yorùbá', 'adunni']},
    'ha': {'name': 'Hausa', 'flag': '🇳🇬', 'voice_keywords': ['hausa', 'harshen hausa', 'salisu']},
    
    # Latin American Languages
    'pt-br': {'name': 'Portuguese (Brazil)', 'flag': '🇧🇷', 'voice_keywords': ['portuguese', 'português brasileiro', 'heloisa']},
    'qu': {'name': 'Quechua', 'flag': '🇵🇪', 'voice_keywords': ['quechua', 'runasimi', 'amaru']},
    'ay': {'name': 'Aymara', 'flag': '🇧🇴', 'voice_keywords': ['aymara', 'aymar aru', 'inti']},
    'gn': {'name': 'Guarani', 'flag': '🇵🇾', 'voice_keywords': ['guarani', 'avañe\'ẽ', 'karai']},
    
    # Additional World Languages
    'sq': {'name': 'Albanian', 'flag': '🇦🇱', 'voice_keywords': ['albanian', 'shqip', 'agron']},
    'az': {'name': 'Azerbaijani', 'flag': '🇦🇿', 'voice_keywords': ['azerbaijani', 'azərbaycan', 'babek']},
    'hy': {'name': 'Armenian', 'flag': '🇦🇲', 'voice_keywords': ['armenian', 'հայերեն', 'ani']},
    'ka': {'name': 'Georgian', 'flag': '🇬🇪', 'voice_keywords': ['georgian', 'ქართული', 'gia']},
    'kk': {'name': 'Kazakh', 'flag': '🇰🇿', 'voice_keywords': ['kazakh', 'қазақ тілі', 'daulet']},
    'ky': {'name': 'Kyrgyz', 'flag': '🇰🇬', 'voice_keywords': ['kyrgyz', 'кыргыз тили', 'gulnara']},
    'tg': {'name': 'Tajik', 'flag': '🇹🇯', 'voice_keywords': ['tajik', 'тоҷикӣ', 'mavluda']},
    'tk': {'name': 'Turkmen', 'flag': '🇹🇲', 'voice_keywords': ['turkmen', 'türkmen dili', 'jemal']},
    'uz': {'name': 'Uzbek', 'flag': '🇺🇿', 'voice_keywords': ['uzbek', 'oʻzbek tili', 'madina']},
    'mn': {'name': 'Mongolian', 'flag': '🇲🇳', 'voice_keywords': ['mongolian', 'монгол хэл', 'batbayar']},
    'bo': {'name': 'Tibetan', 'flag': '🇨🇳', 'voice_keywords': ['tibetan', 'བོད་སྐད', 'tenzin']},
    'dz': {'name': 'Dzongkha', 'flag': '🇧🇹', 'voice_keywords': ['dzongkha', 'རྫོང་ཁ', 'karma']},
    'ii': {'name': 'Yi', 'flag': '🇨🇳', 'voice_keywords': ['yi', 'ꆈꌠꉙ', 'amu']},
    'ug': {'name': 'Uyghur', 'flag': '🇨🇳', 'voice_keywords': ['uyghur', 'ئۇيغۇرچە', 'alim']}
}

def auto_detect_language(text, confidence_threshold=0.7):
    """Enhanced language detection with confidence scoring and multiple methods"""
    if not langdetect_module:
        print("Language detection not available, defaulting to English")
        return 'en', 0.5
    
    try:
        # Primary detection using langdetect
        detected = langdetect_module.detect(text[:2000])  # Use first 2000 chars for accuracy
        
        # Get confidence by detecting multiple samples if text is long enough
        confidence = 0.8  # Default confidence
        
        if len(text) > 1000:
            # Test multiple segments for consistency
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
                        seg_detect = langdetect_module.detect(segment)
                        detections.append(seg_detect)
                    except:
                        continue
            
            # Calculate confidence based on consistency
            if detections:
                most_common = max(set(detections), key=detections.count)
                confidence = detections.count(most_common) / len(detections)
                if confidence >= confidence_threshold:
                    detected = most_common
        
        # Validate detection against supported languages
        if detected in SUPPORTED_LANGUAGES:
            return detected, confidence
        elif detected == 'zh-cn' or detected == 'zh-tw':
            # Handle Chinese variants
            return 'zh' if detected == 'zh-cn' else 'zh-tw', confidence
        else:
            print(f"Detected language '{detected}' not in supported list, defaulting to English")
            return 'en', 0.3
            
    except Exception as e:
        print(f"Language detection error: {str(e)}")
        
        # Fallback: try basic character analysis
        return analyze_text_characters(text)

def analyze_text_characters(text):
    """Fallback language detection based on character patterns"""
    text_sample = text[:1000].lower()
    
    # Character-based detection patterns
    patterns = {
        'zh': r'[\u4e00-\u9fff]',  # Chinese characters
        'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # Japanese hiragana/katakana
        'ko': r'[\uac00-\ud7af]',  # Korean
        'ar': r'[\u0600-\u06ff]',  # Arabic
        'hi': r'[\u0900-\u097f]',  # Hindi/Devanagari
        'ta': r'[\u0b80-\u0bff]',  # Tamil
        'ru': r'[\u0400-\u04ff]',  # Cyrillic
        'th': r'[\u0e00-\u0e7f]',  # Thai
    }
    
    for lang, pattern in patterns.items():
        if re.search(pattern, text_sample):
            return lang, 0.6
    
    # European language detection based on common words
    european_patterns = {
        'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
        'fr': ['le', 'de', 'et', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que'],
        'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
        'it': ['il', 'di', 'che', 'e', 'la', 'per', 'un', 'in', 'con', 'del'],
        'pt': ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para']
    }
    
    words = text_sample.split()
    for lang, common_words in european_patterns.items():
        matches = sum(1 for word in words[:100] if word in common_words)
        if matches > 5:  # Threshold for detection
            return lang, 0.5
    
    return 'en', 0.3  # Default to English

def auto_translate_text(text, target_language=None, auto_detect=True):
    """Enhanced translation with automatic language detection and smart targeting"""
    # Initialize variables to avoid unbound variable issues
    source_language = 'en'  # Default fallback
    confidence = 0.5
    
    if not TRANSLATION_AVAILABLE:
        print("Translation not available, returning original text")
        source_language, confidence = auto_detect_language(text) if langdetect_module else ('en', 0.5)
        return text, source_language, target_language or 'en', confidence
    
    try:
        # Auto-detect source language
        source_language, confidence = auto_detect_language(text)
        print(f"Auto-detected language: {source_language} (confidence: {confidence:.2f})")
        
        # Determine target language
        if not target_language:
            target_language = DEFAULT_TARGET_LANGUAGE
        
        # Skip translation if source and target are the same
        if source_language == target_language:
            print(f"Source and target languages are the same ({source_language}), skipping translation")
            return text, source_language, target_language, confidence
        
        print(f"Translating from {source_language} to {target_language}...")
        
        # Initialize translated_text to handle both code paths
        translated_text = text
        
        # Perform actual translation based on available library
        if USING_DEEP_TRANSLATOR:
            # Use deep-translator with correct instantiation following project memory requirements
            try:
                # Deep Translator must be instantiated with GoogleTranslator(source='auto', target='target_lang') 
                # rather than used as a class reference to avoid 'NoneType' callable errors
                from deep_translator import GoogleTranslator
                
                # Use 'auto' for source language detection as it's more reliable
                translator_instance = GoogleTranslator(source='auto', target=target_language)
                translated_text = translator_instance.translate(text)
                print(f"Deep-translator result: {len(translated_text)} chars")
                
            except Exception as deep_error:
                print(f"Deep-translator error: {str(deep_error)}")
                # Fallback: try with explicit source language
                try:
                    from deep_translator import GoogleTranslator
                    translator_instance = GoogleTranslator(source=source_language, target=target_language)
                    translated_text = translator_instance.translate(text)
                    print(f"Deep-translator with explicit source: {len(translated_text)} chars")
                except Exception as fallback_error:
                    print(f"Deep-translator fallback error: {str(fallback_error)}")
                    return text, source_language, target_language, confidence
        else:
            # Use googletrans - check if googletrans_translator is available
            if googletrans_translator is None:
                print("Googletrans translator not available, returning original text")
                return text, source_language, target_language, confidence
            
            # Split into chunks for better translation
            chunks = split_text_for_translation(text)
            translated_chunks = []
            
            for chunk in chunks:
                if len(chunk.strip()) > 0:
                    try:
                        # Use the already instantiated googletrans translator
                        result = googletrans_translator.translate(text=chunk, src=source_language, dest=target_language)
                        translated_chunks.append(result.text)
                    except Exception as chunk_error:
                        print(f"Chunk translation error: {str(chunk_error)}")
                        translated_chunks.append(chunk)  # Use original if translation fails
            
            translated_text = ' '.join(translated_chunks)
        
        # Validate translation
        if not translated_text or len(translated_text.strip()) < len(text.strip()) * 0.3:
            print("Translation seems too short or empty, using original text")
            return text, source_language, source_language, confidence
        
        print(f"✅ Translation completed: {len(text)} -> {len(translated_text)} characters")
        return translated_text, source_language, target_language, confidence
        
    except Exception as e:
        print(f"Translation error: {str(e)}")
        print("Falling back to original text")
        # Initialize source_language if not defined yet
        if 'source_language' not in locals():
            source_language = auto_detect_language(text)[0] if langdetect_module else 'en'
        return text, source_language, target_language or 'en', 0.0

def split_text_for_translation(text, max_chunk_size=4000):
    """Split text into optimal chunks for translation"""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    sentences = re.split(r'[.!?]+', text)
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If adding this sentence would exceed limit, save current chunk
        if len(current_chunk) + len(sentence) + 2 > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
        else:
            current_chunk += sentence + ". "
    
    # Add remaining chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]

def get_language_info(language_code):
    """Get detailed information about a language"""
    if language_code in SUPPORTED_LANGUAGES:
        lang_info = SUPPORTED_LANGUAGES[language_code]
        return {
            'code': language_code,
            'name': lang_info['name'],
            'flag': lang_info['flag'],
            'voice_keywords': lang_info.get('voice_keywords', []),
            'supported': True
        }
    else:
        return {
            'code': language_code,
            'name': language_code.upper(),
            'flag': '🌐',
            'voice_keywords': [],
            'supported': False
        }

def find_language_specific_voice(language_code, voices):
    """Find the best voice for a specific language"""
    if not language_code or language_code not in SUPPORTED_LANGUAGES:
        return None
    
    lang_info = SUPPORTED_LANGUAGES[language_code]
    voice_keywords = lang_info['voice_keywords']
    
    best_voice = None
    best_score = 0
    
    if voices and isinstance(voices, list):
        for voice in voices:
            if hasattr(voice, 'name') and hasattr(voice, 'id'):
                voice_name = voice.name.lower() if voice.name else ''
                voice_id = voice.id.lower() if voice.id else ''
                
                score = 0
                # Check for language-specific keywords
                for keyword in voice_keywords:
                    if keyword.lower() in voice_name or keyword.lower() in voice_id:
                        score += 20  # High score for language match
                
                # Check for language code in voice info
                if language_code in voice_name or language_code in voice_id:
                    score += 15
                
                # Check if voice has language information
                if hasattr(voice, 'languages') and voice.languages:
                    for lang in voice.languages:
                        if language_code in str(lang).lower():
                            score += 25  # Highest score for direct language support
                
                if score > best_score:
                    best_score = score
                    best_voice = voice.id
    
    return best_voice

def get_available_voices():
    """Get all available system voices with detailed information"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        if voices and isinstance(voices, list):
            for i, voice in enumerate(voices):
                if hasattr(voice, 'name') and hasattr(voice, 'id'):
                    # Determine voice characteristics
                    voice_name = voice.name.lower() if voice.name else ''
                    voice_id = voice.id.lower() if voice.id else ''
                    
                    # Categorize voice
                    category = 'Other'
                    gender = 'Unknown'
                    age_group = 'Adult'
                    
                    # Gender detection
                    female_keywords = ['female', 'woman', 'zira', 'hazel', 'susan', 'cortana', 'eva', 'anna', 'maria']
                    male_keywords = ['male', 'man', 'david', 'mark', 'ryan', 'george', 'james']
                    
                    if any(keyword in voice_name or keyword in voice_id for keyword in female_keywords):
                        gender = 'Female'
                        category = '👩 Female'
                    elif any(keyword in voice_name or keyword in voice_id for keyword in male_keywords):
                        gender = 'Male'
                        category = '👨 Male'
                    
                    # Age detection
                    young_keywords = ['young', 'child', 'kid', 'boy', 'girl']
                    if any(keyword in voice_name or keyword in voice_id for keyword in young_keywords):
                        age_group = 'Young'
                        category = '👧👦 Young' if gender == 'Unknown' else f'👧👦 Young {gender}'
                    
                    # Quality detection
                    quality = 'Standard'
                    if any(keyword in voice_name for keyword in ['premium', 'enhanced', 'natural', 'neural']):
                        quality = 'High'
                    
                    voice_info = {
                        'id': voice.id,
                        'name': voice.name if voice.name else f'Voice {i+1}',
                        'display_name': voice.name if voice.name else f'System Voice {i+1}',
                        'category': category,
                        'gender': gender,
                        'age_group': age_group,
                        'quality': quality,
                        'languages': getattr(voice, 'languages', ['en']),
                        'index': i
                    }
                    voice_list.append(voice_info)
        
        return voice_list
    except Exception as e:
        print(f"Error getting voices: {str(e)}")
        return []

def text_to_speech(text, output_path, voice_rate=175, voice_volume=0.9, voice_id=None, voice_type='female_warm', target_language='en', enable_naturalness=True, continuous_flow=True, enable_ai_features=True):
    """Convert text to speech with advanced naturalness and emotion detection"""
    try:
        engine = pyttsx3.init()
        
        # Analyze text for emotional content if naturalness is enabled
        emotion = 'neutral'
        intensity = 0.5
        
        if enable_naturalness:
            emotion, intensity = analyze_text_emotion(text)
            print(f"Detected emotion: {emotion} (intensity: {intensity:.2f})")
        
        # Get natural voice settings based on emotion
        natural_settings = get_natural_voice_settings(emotion, intensity, voice_rate, voice_volume)
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        selected_voice = None
        
        # Voice selection logic (keeping existing logic)
        voice_preferences = {
            'female_warm': {
                'keywords': ['zira', 'hazel', 'susan', 'female', 'woman', 'cortana', 'eva'],
                'avoid': ['male', 'man', 'david', 'mark'],
                'pitch_mod': 0,
                'rate_mod': 0
            },
            'female_young': {
                'keywords': ['zira', 'hazel', 'female', 'woman', 'young', 'girl'],
                'avoid': ['male', 'man', 'old', 'mature'],
                'pitch_mod': 20,
                'rate_mod': 15
            },
            'female_mature': {
                'keywords': ['susan', 'female', 'woman', 'mature', 'elder'],
                'avoid': ['male', 'man', 'young', 'girl'],
                'pitch_mod': -10,
                'rate_mod': -20
            },
            'male_deep': {
                'keywords': ['david', 'mark', 'male', 'man', 'deep', 'bass'],
                'avoid': ['female', 'woman', 'high', 'soprano'],
                'pitch_mod': -15,
                'rate_mod': -10
            },
            'male_young': {
                'keywords': ['male', 'man', 'young', 'boy', 'teen'],
                'avoid': ['female', 'woman', 'old', 'mature'],
                'pitch_mod': 10,
                'rate_mod': 10
            },
            'male_mature': {
                'keywords': ['david', 'mark', 'male', 'man', 'mature', 'elder'],
                'avoid': ['female', 'woman', 'young', 'boy'],
                'pitch_mod': -20,
                'rate_mod': -25
            },
            'child_female': {
                'keywords': ['female', 'girl', 'child', 'young', 'kid'],
                'avoid': ['male', 'man', 'adult', 'mature'],
                'pitch_mod': 40,
                'rate_mod': 25
            },
            'child_male': {
                'keywords': ['male', 'boy', 'child', 'young', 'kid'],
                'avoid': ['female', 'woman', 'adult', 'mature'],
                'pitch_mod': 30,
                'rate_mod': 20
            },
            'narrator_professional': {
                'keywords': ['david', 'mark', 'susan', 'professional', 'clear'],
                'avoid': ['robotic', 'synthetic'],
                'pitch_mod': 0,
                'rate_mod': -5
            },
            'storyteller_dramatic': {
                'keywords': ['zira', 'hazel', 'dramatic', 'expressive'],
                'avoid': ['monotone', 'flat'],
                'pitch_mod': 5,
                'rate_mod': -15
            }
        }
        
        # If specific voice ID is provided, use it directly
        if voice_id:
            if voices and isinstance(voices, list):
                for voice in voices:
                    if hasattr(voice, 'id') and voice.id == voice_id:
                        selected_voice = voice_id
                        break
        
        # Try to find language-specific voice if target language is specified
        if not selected_voice and target_language != 'en':
            language_voice = find_language_specific_voice(target_language, voices)
            if language_voice:
                selected_voice = language_voice
                print(f"Selected language-specific voice for {target_language}: {selected_voice}")
        
        # Use voice packs for better voice selection
        if not selected_voice and voice_type in VOICE_PACKS:
            voice_pack = VOICE_PACKS[voice_type]
            best_score = 0
            
            if voices and isinstance(voices, list):
                for voice in voices:
                    if hasattr(voice, 'name') and hasattr(voice, 'id'):
                        voice_name = voice.name.lower() if voice.name else ''
                        voice_id_lower = voice.id.lower() if voice.id else ''
                        
                        score = 0
                        
                        # Positive points for matching keywords
                        for keyword in voice_pack['keywords']:
                            if keyword in voice_name or keyword in voice_id_lower:
                                score += 10
                        
                        # Negative points for avoid keywords
                        for avoid_word in voice_pack['avoid']:
                            if avoid_word in voice_name or avoid_word in voice_id_lower:
                                score -= 5
                        
                        # Bonus for personality matching
                        personality = voice_pack.get('personality', '')
                        if personality in voice_name or personality in voice_id_lower:
                            score += 15
                        
                        if score > best_score:
                            best_score = score
                            selected_voice = voice.id
                
                # Fallback to first available voice if no good match
                if not selected_voice and len(voices) > 0 and hasattr(voices[0], 'id'):
                    selected_voice = voices[0].id
        else:
            # Fallback to original voice preferences for unknown voice types
            voice_pref = voice_preferences.get(voice_type, voice_preferences['female_warm'])
            
            best_score = 0
            
            if voices and isinstance(voices, list):
                for voice in voices:
                    if hasattr(voice, 'name') and hasattr(voice, 'id'):
                        voice_name = voice.name.lower() if voice.name else ''
                        voice_id_lower = voice.id.lower() if voice.id else ''
                        
                        score = 0
                        
                        # Positive points for matching keywords
                        for keyword in voice_pref['keywords']:
                            if keyword in voice_name or keyword in voice_id_lower:
                                score += 10
                        
                        # Negative points for avoid keywords
                        for avoid_word in voice_pref['avoid']:
                            if avoid_word in voice_name or avoid_word in voice_id_lower:
                                score -= 5
                        
                        # Prefer voices with more detailed information
                        if len(voice_name) > 5:
                            score += 2
                        
                        if score > best_score:
                            best_score = score
                            selected_voice = voice.id
                
                # Fallback to first available voice if no good match
                if not selected_voice and len(voices) > 0 and hasattr(voices[0], 'id'):
                    selected_voice = voices[0].id
        
        if selected_voice:
            engine.setProperty('voice', selected_voice)
        
        # Use natural voice settings
        engine.setProperty('rate', natural_settings['rate'])
        engine.setProperty('volume', natural_settings['volume'])
        
        # Process text for naturalness
        if enable_naturalness:
            processed_text = enhance_text_naturalness(text, emotion, intensity)
        else:
            processed_text = enhance_text_for_speech(text, voice_type)
        
        # Apply language-specific enhancements if target language is specified
        if target_language and target_language != 'en':
            processed_text = enhance_text_for_language(processed_text, target_language)
        
        print(f"Generating speech with emotion: {emotion}, intensity: {intensity:.2f}")
        print(f"Voice settings - Rate: {natural_settings['rate']}, Volume: {natural_settings['volume']:.2f}")
        
        engine.save_to_file(processed_text, output_path)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"Error converting text to speech: {str(e)}")
        return False

def enhance_text_for_speech(text, voice_type='female_warm'):
    """Enhance text with punctuation and pauses for more natural speech based on voice type"""
    import re
    
    # Base text enhancement
    text = re.sub(r'([.!?])\s+', r'\1... ', text)
    text = re.sub(r'(,)\s+', r'\1 ', text)
    
    # Voice type specific enhancements
    if 'child' in voice_type:
        # Children voices - more excitement and pauses
        text = re.sub(r'(!+)', r'!! ... ', text)
        text = re.sub(r'(\?)\s+', r'? ... ', text)
        text = re.sub(r'"([^"]+)"', r'... "\1" ... ', text)
    elif 'dramatic' in voice_type or 'storyteller' in voice_type:
        # Dramatic voices - longer pauses and emphasis
        text = re.sub(r'([.!?])\s+', r'\1.... ', text)
        text = re.sub(r'"([^"]+)"', r'..... "\1" ..... ', text)
        text = re.sub(r'\s*[-\u2013\u2014]\s*', ' ..... ', text)
    elif 'professional' in voice_type or 'narrator' in voice_type:
        # Professional voices - clear, measured delivery
        text = re.sub(r'([.])\s+', r'\1.. ', text)
        text = re.sub(r'([!?])\s+', r'\1... ', text)
    elif 'young' in voice_type:
        # Young voices - energetic with shorter pauses
        text = re.sub(r'([.!?])\s+', r'\1.. ', text)
        text = re.sub(r'(!+)', r'! .. ', text)
    elif 'mature' in voice_type:
        # Mature voices - slower, more deliberate
        text = re.sub(r'([.!?])\s+', r'\1.... ', text)
        text = re.sub(r'(,)\s+', r'\1.. ', text)
    
    # Add pauses before and after dashes for dramatic effect
    text = re.sub(r'\s*[-\u2013\u2014]\s*', ' ... ', text)
    
    # Break up long sentences with breathing pauses
    sentences = text.split('. ')
    enhanced_sentences = []
    
    for sentence in sentences:
        # Add micro-pauses in long sentences for child and dramatic voices
        if len(sentence) > 80 and ('child' in voice_type or 'dramatic' in voice_type):
            sentence = re.sub(r'\b(and|but|or|so|yet|for|nor|because|since|although|while|when|where|if|unless)\s+', 
                            r'\1... ', sentence)
        elif len(sentence) > 120:  # For other voice types
            sentence = re.sub(r'\b(and|but|or|so|yet|for|nor|because|since|although|while|when|where|if|unless)\s+', 
                            r'\1.. ', sentence)
        enhanced_sentences.append(sentence)
    
    return '. '.join(enhanced_sentences)

def enhance_text_for_language(text, language_code):
    """Apply language-specific text enhancements for better pronunciation"""
    import re
    
    if not language_code or language_code == 'en':
        return text
    
    # Tamil and other Indic languages - add natural pauses for better pronunciation
    if language_code in ['ta', 'hi', 'te', 'kn', 'ml', 'mr', 'gu', 'pa', 'or', 'as', 'bn']:
        # Add pauses after complex consonant clusters
        text = re.sub(r'([\u0B80-\u0BFF]{3,})', r'\1 ', text)  # Tamil
        text = re.sub(r'([\u0900-\u097F]{3,})', r'\1 ', text)  # Devanagari (Hindi/Marathi)
        text = re.sub(r'([\u0C00-\u0C7F]{3,})', r'\1 ', text)  # Telugu
        text = re.sub(r'([\u0C80-\u0CFF]{3,})', r'\1 ', text)  # Kannada
        text = re.sub(r'([\u0D00-\u0D7F]{3,})', r'\1 ', text)  # Malayalam
        # Add slight pause after common conjunctive particles
        text = re.sub(r'([\u0964\u0965])', r'\1.. ', text)  # Devanagari danda
        
    # Arabic and Hebrew - handle RTL text flow
    elif language_code in ['ar', 'he', 'fa', 'ur']:
        # Add pauses for better flow in RTL languages
        text = re.sub(r'([\u0600-\u06FF]{4,})', r'\1 ', text)  # Arabic
        text = re.sub(r'([\u0590-\u05FF]{4,})', r'\1 ', text)  # Hebrew
        
    # Chinese and Japanese - add pauses for tonal clarity
    elif language_code in ['zh', 'zh-tw', 'ja']:
        # Add micro-pauses for tonal languages
        text = re.sub(r'([\u4e00-\u9fff]{4,})', r'\1 ', text)  # Chinese characters
        text = re.sub(r'([\u3040-\u309f\u30a0-\u30ff]{3,})', r'\1 ', text)  # Japanese hiragana/katakana
        
    # Korean - handle syllable blocks
    elif language_code == 'ko':
        text = re.sub(r'([\uac00-\ud7af]{4,})', r'\1 ', text)  # Korean syllables
        
    # Thai and other Southeast Asian languages
    elif language_code in ['th', 'my', 'km', 'lo']:
        # Add pauses for better pronunciation in complex scripts
        text = re.sub(r'([\u0e00-\u0e7f]{4,})', r'\1 ', text)  # Thai
        text = re.sub(r'([\u1000-\u109f]{4,})', r'\1 ', text)  # Myanmar
        text = re.sub(r'([\u1780-\u17ff]{4,})', r'\1 ', text)  # Khmer
        
    return text

@app.route('/')
def index():
    """Main interface - Serve the classic Flask interface"""
    # Check if Streamlit is available
    try:
        import streamlit
        from pathlib import Path
        
        # Launch EchoVerse Streamlit app
        echoverse_app = Path(__file__).parent / 'echoverse_app.py'
        if echoverse_app.exists():
            return jsonify({
                'message': 'EchoVerse Streamlit interface is the primary application',
                'streamlit_url': 'http://localhost:8501',
                'launch_command': 'streamlit run echoverse_app.py',
                'flask_classic': 'http://192.168.39.10:5000/classic'
            })
        else:
            # Fallback to Flask if Streamlit app not available
            return render_template('index_new.html', is_author=is_author())
            
    except ImportError:
        # Fallback to Flask if Streamlit not available
        return render_template('index_new.html', is_author=is_author())

@app.route('/classic')
def classic_interface():
    return render_template('index.html', is_author=is_author())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = username
            return jsonify({'success': True, 'role': user['role']})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '' or file.filename is None:
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from the uploaded file
        text = extract_text_from_file(filepath)
        if text is None:
            return jsonify({'error': 'Failed to extract text from file'}), 500
        
        if len(text.strip()) == 0:
            return jsonify({'error': 'No text found in the file'}), 400
        
        # Generate unique filename for audio
        audio_filename = f"audiobook_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        
        # Get voice settings with enhanced options
        voice_rate = request.form.get('voice_rate', 175, type=int)
        voice_volume = request.form.get('voice_volume', 0.9, type=float)
        voice_type = request.form.get('voice_type', 'female_warm', type=str)
        voice_id = request.form.get('voice_id', None, type=str)
        target_language = request.form.get('target_language', 'en', type=str)
        enable_naturalness = request.form.get('enable_naturalness', 'true') == 'true'
        continuous_flow = request.form.get('continuous_flow', 'true') == 'true'
        enable_ai_features = request.form.get('enable_ai_features', 'true') == 'true'
        enable_translation = request.form.get('enable_translation', 'true') == 'true'  # Default to enabled
        
        # Auto-detect and translate text by default
        original_language = None
        translation_performed = False
        
        # Always auto-detect language first
        detected_lang, confidence = auto_detect_language(text)
        print(f"Auto-detected language: {detected_lang} (confidence: {confidence:.2f})")
        
        # Determine if translation should be performed
        should_translate = False
        
        if enable_translation:
            if target_language == 'auto':
                # Keep original language, no translation
                target_language = detected_lang
                print(f"Auto mode: keeping original language {detected_lang}")
            elif target_language != detected_lang:
                # Translate to target language
                should_translate = True
                print(f"Translation needed: {detected_lang} -> {target_language}")
            else:
                print(f"Source and target languages are the same ({detected_lang}), no translation needed")
        else:
            print("Translation disabled by user")
        
        # Perform translation if needed
        if should_translate:
            print(f"🔄 Starting translation: {detected_lang} → {target_language}")
            translated_text, source_lang, final_lang, trans_confidence = auto_translate_text(text, target_language, True)
            if translated_text != text and trans_confidence > 0.3:
                text = translated_text
                original_language = source_lang
                translation_performed = True
                print(f"✅ Translation completed: {source_lang} → {final_lang} (confidence: {trans_confidence:.2f})")
                print(f"📝 Translated text preview: {text[:100]}...")
            else:
                print(f"❌ Translation not applied - confidence: {trans_confidence:.2f}, text changed: {translated_text != text}")
        else:
            print(f"⏭️ No translation needed")
        
        # Store the original target language for response data
        original_target_language = target_language
        
        # For voice selection, use target language if translation was performed,
        # otherwise use detected language for voice matching
        voice_language = target_language if translation_performed else detected_lang
        
        # Handle 'auto' mode for voice selection
        if original_target_language == 'auto':
            voice_language = detected_lang
        
        # Generate story analysis for AI features (only if AI is enabled)
        story_analysis = None
        story_questions = None
        
        if enable_ai_features:
            story_analysis = analyze_story_content(text)
            story_questions = generate_story_questions(text)
        
        # Convert text to speech with enhanced options
        success = text_to_speech(text, audio_path, voice_rate, voice_volume, voice_id, voice_type, voice_language, enable_naturalness, continuous_flow, enable_ai_features)
        
        if success:
            response_data = {
                'success': True,
                'message': 'Audiobook generated successfully with enhanced voice options!',
                'audio_file': audio_filename,
                'text_preview': text[:500] + '...' if len(text) > 500 else text,
                'continuous_flow': continuous_flow,
                'ai_features_enabled': enable_ai_features,
                'detected_language': detected_lang,
                'target_language': original_target_language,  # Use original target language
                'translation_performed': translation_performed,
                'original_language': original_language,
                'language_confidence': confidence
            }
            
            # Add AI features only if enabled
            if enable_ai_features and story_analysis and story_questions:
                response_data.update({
                    'story_analysis': story_analysis,
                    'story_questions': story_questions,
                    'emotion_detected': analyze_text_emotion(text)[0],
                    'emotion_intensity': round(analyze_text_emotion(text)[1], 2)
                })
            
            return jsonify(response_data)
        else:
            return jsonify({'error': 'Failed to generate audiobook'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload TXT, PDF, or DOCX files.'}), 400

@app.route('/ask-story', methods=['POST'])
def ask_story_question():
    """AI-powered story Q&A system"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        text = data.get('text', '')
        question = data.get('question', '')
        
        if not text or not question:
            return jsonify({'error': 'Both text and question are required'}), 400
        
        # Generate AI insight
        insight = provide_story_insights(text, question)
        
        # Also provide story analysis if requested
        include_analysis = data.get('include_analysis', False)
        response: dict = {'insight': insight}
        
        if include_analysis:
            response['analysis'] = analyze_story_content(text)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'error': f'Story analysis failed: {str(e)}'}), 500

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    """Generate story discussion questions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        questions = generate_story_questions(text)
        analysis = analyze_story_content(text)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'error': f'Question generation failed: {str(e)}'}), 500

@app.route('/upload-voice-sample', methods=['POST'])
def upload_voice_sample():
    """Upload voice sample for cloning (authors only)"""
    if not is_author():
        return jsonify({'error': 'Voice cloning is only available to authors'}), 403
    
    if 'voice_sample' not in request.files:
        return jsonify({'error': 'No voice sample provided'}), 400
    
    file = request.files['voice_sample']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file format (basic validation)
    allowed_audio_formats = {'wav', 'mp3', 'flac', 'm4a'}
    filename = file.filename
    if not filename or not ('.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_audio_formats):
        return jsonify({'error': 'Invalid audio format. Please upload WAV, MP3, FLAC, or M4A files.'}), 400
    
    # Save voice sample
    filename = secure_filename(f"voice_sample_{session['user_id']}_{uuid.uuid4().hex[:8]}.wav")
    filepath = os.path.join(app.config['VOICE_SAMPLES_FOLDER'], filename)
    file.save(filepath)
    
    # Store voice sample info in user data
    user_id = session['user_id']
    if 'voice_samples' not in users_db[user_id]:
        users_db[user_id]['voice_samples'] = []
    
    users_db[user_id]['voice_samples'].append({
        'filename': filename,
        'uploaded_at': datetime.now().isoformat(),
        'original_name': file.filename
    })
    
    return jsonify({
        'success': True,
        'message': 'Voice sample uploaded successfully!',
        'sample_id': filename,
        'note': 'Voice cloning feature is in development. Currently using advanced voice synthesis.'
    })

@app.route('/get-voice-samples')
def get_voice_samples():
    """Get user's voice samples (authors only)"""
    if not is_author():
        return jsonify({'error': 'Access denied'}), 403
    
    user_id = session['user_id']
    samples = users_db[user_id].get('voice_samples', [])
    
    return jsonify({
        'success': True,
        'samples': samples
    })

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve audio files"""
    audio_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/wav')
    return "Audio file not found", 404

@app.route('/preview-voice', methods=['POST'])
def preview_voice():
    """Generate a short voice preview with naturalness"""
    try:
        voice_type = request.form.get('voice_type', 'female_warm', type=str)
        voice_rate = request.form.get('voice_rate', 175, type=int)
        voice_volume = request.form.get('voice_volume', 0.9, type=float)
        voice_id = request.form.get('voice_id', None, type=str)
        target_language = request.form.get('target_language', 'en', type=str)
        enable_naturalness = request.form.get('enable_naturalness', 'true') == 'true'
        
        # Enhanced sample texts with emotional content
        sample_texts = {
            'female_warm': "Hello! I'm your warm, caring narrator. I'll bring your stories to life with genuine emotion and natural flow, making every word feel authentic and engaging.",
            'female_young': "Hi there! I'm full of energy and excitement! I love telling amazing adventures with enthusiasm and joy that will captivate young listeners!",
            'female_mature': "Good day. I'm here to share wisdom and knowledge with elegant clarity and sophisticated grace, perfect for mature storytelling.",
            'male_deep': "Greetings. My rich, resonant voice will captivate listeners with powerful, dramatic storytelling that commands attention.",
            'male_young': "Hey! I'm your modern voice, ready to tackle contemporary tales with clear energy and natural charm.",
            'male_mature': "Good afternoon. I provide authoritative, professional narration with the wisdom of experience and measured delivery.",
            'child_female': "Hi! I'm a happy little voice perfect for magical fairy tales! Every story becomes a wonderful adventure full of wonder and joy!",
            'child_male': "Hello! I love telling exciting adventure stories with lots of energy and fun! Let's go on amazing journeys together!",
            'narrator_professional': "Welcome. I deliver crystal-clear, professional narration optimized for audiobooks, ensuring every word is perfectly understood.",
            'storyteller_dramatic': "Behold! I am your theatrical voice, ready to enchant audiences with dramatic flair, emotional depth, and captivating storytelling magic!"
        }
        
        sample_text = sample_texts.get(voice_type, sample_texts['female_warm'])
        
        # Add emotion-specific text for naturalness preview
        if enable_naturalness:
            emotion_samples = {
                'excitement': "This is absolutely incredible! What an amazing discovery that will change everything!",
                'mystery': "Something strange is happening... hidden secrets wait in the shadows, ready to be revealed...",
                'romance': "Love filled her heart as she gazed into his tender eyes, feeling the gentle warmth of true affection.",
                'adventure': "Suddenly, they rushed forward on the most thrilling quest of their lives!"
            }
            
            # Add an emotional sample to demonstrate naturalness
            emotion_demo = list(emotion_samples.values())[hash(voice_type) % len(emotion_samples)]
            sample_text += " " + emotion_demo
        
        # Translate sample text if target language is specified
        if target_language and target_language != 'en':
            translated_sample, _, _, _ = auto_translate_text(sample_text, target_language)
            if translated_sample != sample_text:
                sample_text = translated_sample
        
        # Generate unique filename for preview
        preview_filename = f"preview_{voice_type}_{target_language}_{uuid.uuid4().hex[:6]}.wav"
        preview_path = os.path.join(app.config['AUDIO_FOLDER'], preview_filename)
        
        # Generate preview audio with naturalness
        success = text_to_speech(sample_text, preview_path, voice_rate, voice_volume, voice_id, voice_type, target_language, enable_naturalness)
        
        if success:
            # Analyze the sample for emotion feedback
            emotion, intensity = analyze_text_emotion(sample_text) if enable_naturalness else ('neutral', 0.5)
            
            return jsonify({
                'success': True,
                'preview_file': preview_filename,
                'sample_text': sample_text,
                'emotion_detected': emotion,
                'emotion_intensity': round(intensity, 2),
                'naturalness_enabled': enable_naturalness
            })
        else:
            return jsonify({'error': 'Failed to generate voice preview'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Preview generation failed: {str(e)}'}), 500

@app.route('/get-languages')
def get_languages():
    """Get all supported languages for translation"""
    return jsonify({
        'success': True,
        'languages': SUPPORTED_LANGUAGES,
        'translation_available': TRANSLATION_AVAILABLE
    })

@app.route('/translate', methods=['POST'])
def translate_text_api():
    """Translate text to target language API endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        text_content = data.get('text', '')
        target_language = data.get('target_language', 'en')
        source_language = data.get('source_language', 'auto')
        
        if not text_content.strip():
            return jsonify({'error': 'No text content provided'}), 400
        
        # Perform translation using existing function
        translated_text, detected_source, actual_target, confidence = auto_translate_text(
            text_content, target_language, auto_detect=True
        )
        
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'source_language': detected_source,
            'target_language': actual_target,
            'confidence': confidence
        })
        
    except Exception as e:
        print(f"Translation API error: {str(e)}")
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

@app.route('/detect-language', methods=['POST'])
def detect_text_language():
    """Detect language of uploaded text or file"""
    try:
        # Check if text is provided directly in form data
        text = request.form.get('text', '')
        
        # If no form text, check for JSON data
        if not text:
            data = request.get_json()
            if data:
                text = data.get('text', '')
        
        # If no direct text, check for uploaded file
        if not text and 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if file_ext in ALLOWED_EXTENSIONS:
                    # Save temporary file
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_detect_{filename}')
                    file.save(temp_path)
                    
                    try:
                        # Extract text using the same function as main processing
                        text = extract_text_from_file(temp_path)
                        if not text:
                            return jsonify({'error': 'Could not extract text from file'}), 400
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                else:
                    return jsonify({'error': f'Unsupported file type: {file_ext}'}), 400
        
        if not text or len(text.strip()) < 10:
            return jsonify({'error': 'Insufficient text for language detection (minimum 10 characters)'}), 400
        
        # Perform language detection
        detected, confidence = auto_detect_language(text[:1000])  # Use first 1000 chars for detection
        language_info = SUPPORTED_LANGUAGES.get(detected, SUPPORTED_LANGUAGES['en'])
        
        return jsonify({
            'success': True,
            'detected_language': detected,
            'language_name': language_info['name'],
            'language_flag': language_info['flag'],
            'confidence': confidence,
            'text_preview': text[:100] + '...' if len(text) > 100 else text
        })
        
    except Exception as e:
        print(f"Language detection error: {str(e)}")
        return jsonify({'error': f'Language detection failed: {str(e)}'}), 500

@app.route('/get-voices')
def get_voices():
    """Get all available voices with categorization"""
    try:
        voices = get_available_voices()
        
        # Group voices by category
        categorized_voices = {}
        for voice in voices:
            category = voice['category']
            if category not in categorized_voices:
                categorized_voices[category] = []
            categorized_voices[category].append(voice)
        
        return jsonify({
            'success': True,
            'voices': voices,
            'categorized': categorized_voices,
            'count': len(voices)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/voices')
def list_voices():
    """List all available TTS voices for debugging"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        if voices and isinstance(voices, list):
            for i, voice in enumerate(voices):
                if hasattr(voice, 'name') and hasattr(voice, 'id'):
                    voice_info = {
                        'index': i,
                        'name': voice.name if voice.name else 'Unknown',
                        'id': voice.id if voice.id else 'Unknown',
                        'languages': getattr(voice, 'languages', ['Unknown'])
                    }
                    voice_list.append(voice_info)
        
        return jsonify({
            'success': True,
            'voices': voice_list,
            'count': len(voice_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/files')
def list_files():
    """List all generated audio files"""
    audio_files = []
    if os.path.exists(app.config['AUDIO_FOLDER']):
        for filename in os.listdir(app.config['AUDIO_FOLDER']):
            if filename.endswith('.wav'):
                file_path = os.path.join(app.config['AUDIO_FOLDER'], filename)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                audio_files.append({
                    'filename': filename,
                    'size': f"{file_size / 1024 / 1024:.2f} MB",
                    'created': file_time.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return render_template('files.html', audio_files=audio_files)

@app.route('/debug-translation')
def debug_translation():
    """Debug page for translation issues"""
    return render_template('debug_translation.html')

@app.route('/api/upload', methods=['POST'])
def api_upload_file_endpoint():
    """API endpoint for file upload"""
    return upload_file()

@app.route('/api/detect-language', methods=['POST'])
def api_detect_language():
    """API endpoint for language detection"""
    return detect_text_language()

@app.route('/api/translate', methods=['POST'])
def api_translate():
    """API endpoint for text translation"""
    return translate_text_api()

@app.route('/api/voices')
def api_get_voices():
    """API endpoint for getting available voices"""
    return get_voices()

@app.route('/api/voice-preview', methods=['POST'])
def api_preview_voice():
    """API endpoint for voice preview"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        voice_type = data.get('voice_type', 'female_warm')
        voice_rate = data.get('voice_rate', 175)
        voice_volume = data.get('voice_volume', 0.9)
        voice_id = data.get('voice_id', None)
        target_language = data.get('target_language', 'en')
        enable_naturalness = data.get('enable_naturalness', True)
        
        # Enhanced sample texts with emotional content
        sample_texts = {
            'female_warm': "Hello! I'm your warm, caring narrator. I'll bring your stories to life with genuine emotion and natural flow, making every word feel authentic and engaging.",
            'female_young': "Hi there! I'm full of energy and excitement! I love telling amazing adventures with enthusiasm and joy that will captivate young listeners!",
            'female_mature': "Good day. I'm here to share wisdom and knowledge with elegant clarity and sophisticated grace, perfect for mature storytelling.",
            'male_deep': "Greetings. My rich, resonant voice will captivate listeners with powerful, dramatic storytelling that commands attention.",
            'male_young': "Hey! I'm your modern voice, ready to tackle contemporary tales with clear energy and natural charm.",
            'male_mature': "Good afternoon. I provide authoritative, professional narration with the wisdom of experience and measured delivery.",
            'child_female': "Hi! I'm a happy little voice perfect for magical fairy tales! Every story becomes a wonderful adventure full of wonder and joy!",
            'child_male': "Hello! I love telling exciting adventure stories with lots of energy and fun! Let's go on amazing journeys together!",
            'narrator_professional': "Welcome. I deliver crystal-clear, professional narration optimized for audiobooks, ensuring every word is perfectly understood.",
            'storyteller_dramatic': "Behold! I am your theatrical voice, ready to enchant audiences with dramatic flair, emotional depth, and captivating storytelling magic!"
        }
        
        sample_text = sample_texts.get(voice_type, sample_texts['female_warm'])
        
        # Add emotion-specific text for naturalness preview
        if enable_naturalness:
            emotion_samples = {
                'excitement': "This is absolutely incredible! What an amazing discovery that will change everything!",
                'mystery': "Something strange is happening... hidden secrets wait in the shadows, ready to be revealed...",
                'romance': "Love filled her heart as she gazed into his tender eyes, feeling the gentle warmth of true affection.",
                'adventure': "Suddenly, they rushed forward on the most thrilling quest of their lives!"
            }
            
            # Add an emotional sample to demonstrate naturalness
            emotion_demo = list(emotion_samples.values())[hash(voice_type) % len(emotion_samples)]
            sample_text += " " + emotion_demo
        
        # Translate sample text if target language is specified
        if target_language and target_language != 'en':
            translated_sample, _, _, _ = auto_translate_text(sample_text, target_language)
            if translated_sample != sample_text:
                sample_text = translated_sample
        
        # Generate unique filename for preview
        preview_filename = f"preview_{voice_type}_{target_language}_{uuid.uuid4().hex[:6]}.wav"
        preview_path = os.path.join(app.config['AUDIO_FOLDER'], preview_filename)
        
        # Generate preview audio with naturalness
        success = text_to_speech(sample_text, preview_path, voice_rate, voice_volume, voice_id, voice_type, target_language, enable_naturalness)
        
        if success:
            # Analyze the sample for emotion feedback
            emotion, intensity = analyze_text_emotion(sample_text) if enable_naturalness else ('neutral', 0.5)
            
            return jsonify({
                'success': True,
                'preview_file': preview_filename,
                'sample_text': sample_text,
                'emotion_detected': emotion,
                'emotion_intensity': round(intensity, 2),
                'naturalness_enabled': enable_naturalness
            })
        else:
            return jsonify({'error': 'Failed to generate voice preview'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Preview generation failed: {str(e)}'}), 500

@app.route('/api/analyze-text', methods=['POST'])
def api_analyze_text():
    """API endpoint for text analysis"""
    try:
        data = request.get_json()
        text_content = data.get('text', '')
        
        if not text_content.strip():
            return jsonify({'error': 'No text content provided'}), 400
        
        # Perform text analysis using existing functions
        emotion, intensity = analyze_text_emotion(text_content)
        story_analysis = analyze_story_content(text_content)
        
        return jsonify({
            'word_count': len(text_content.split()),
            'sentence_count': len(re.findall(r'[.!?]+', text_content)),
            'reading_level': 'intermediate',
            'genre_hints': story_analysis.get('genre_hints', []),
            'themes': story_analysis.get('themes', []),
            'characters': story_analysis.get('characters', []),
            'emotion_analysis': {
                'dominant_emotion': emotion,
                'intensity': intensity,
                'confidence': 0.8
            }
        })
    except Exception as e:
        return jsonify({'error': f'Text analysis failed: {str(e)}'}), 500

@app.route('/api/generate-audio', methods=['POST'])
def api_generate_audio():
    """API endpoint for audiobook generation"""
    try:
        data = request.get_json()
        text_content = data.get('text', '')
        settings = data.get('settings', {})
        
        if not text_content.strip():
            return jsonify({'error': 'No text content provided'}), 400
        
        # Generate unique filename for audio
        audio_filename = f"audiobook_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        
        # Get voice settings
        voice_rate = settings.get('rate', 175)
        voice_volume = settings.get('volume', 0.9)
        voice_id = settings.get('voice_id', None)
        personality = settings.get('personality', 'narrator')
        
        # Convert text to speech
        success = text_to_speech(
            text_content, audio_path, voice_rate, voice_volume, 
            voice_id, personality, 'en', True, True, True
        )
        
        if success:
            return jsonify({
                'success': True,
                'audio_file': audio_filename,
                'audio_path': audio_path
            })
        else:
            return jsonify({'error': 'Failed to generate audiobook'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Audio generation failed: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def api_download_file(filename):
    """API endpoint for downloading audio files"""
    return serve_audio(filename)

@app.route('/api/status')
def api_status():
    """API endpoint for application status"""
    try:
        # Test if services are working
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        return jsonify({
            'application': 'running',
            'services': {
                'tts_service': 'healthy' if voices else 'unhealthy',
                'translation_service': 'healthy' if TRANSLATION_AVAILABLE else 'unhealthy',
                'language_detection': 'healthy' if langdetect_module else 'unhealthy'
            }
        })
    except Exception as e:
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)