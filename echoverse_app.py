"""
EchoVerse - An AI-Powered Audiobook Creation Tool
Built with Streamlit and IBM Watson Services
"""

import streamlit as st
import os
import tempfile
import base64
import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local services
from services.ibm_watson_service import IBMWatsonService
from services.echoverse_text_service import EchoVerseTextService
from services.echoverse_audio_service import EchoVerseAudioService

# Page configuration
st.set_page_config(
    page_title="EchoVerse - AI Audiobook Creator",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .text-panel {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-panel {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-panel {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-panel {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .audio-controls {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class EchoVerseApp:
    """Main EchoVerse Streamlit application"""
    
    def __init__(self):
        try:
            self.watson_service = IBMWatsonService()
            self.text_service = EchoVerseTextService()
            self.audio_service = EchoVerseAudioService()
            self._initialize_session_state()
            self._check_api_credentials()
            # Languages with known limited support
            self.limited_support_languages = {
                "Tamil": "ta",
                "Hindi": "hi", 
                "Russian": "ru",
                "Arabic": "ar",
                "Korean": "ko",
                "Turkish": "tr",
                "Thai": "th",
                "Vietnamese": "vi"
            }
        except Exception as e:
            st.error(f"Failed to initialize EchoVerse services: {e}")
            logger.error(f"Initialization error: {e}")
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        defaults = {
            'original_text': "",
            'rewritten_text': "",
            'translated_text': "",
            'selected_tone': "Neutral",
            'selected_voice': "Lisa",
            'target_language': "Spanish",
            'audio_data': None,
            'translated_audio_data': None,
            'processing_status': "",
            'api_status_checked': False,
            'show_advanced_options': False,
            'speech_speed': 1.0,
            'audio_quality': "High",
            'last_rewrite_time': 0,
            'last_translation_time': 0
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _check_api_credentials(self):
        """Check if IBM Watson API credentials are configured"""
        if st.session_state.api_status_checked:
            return
            
        missing_creds = []
        if not os.getenv('IBM_TTS_API_KEY'):
            missing_creds.append('IBM_TTS_API_KEY')
        if not os.getenv('IBM_TRANSLATOR_API_KEY'):
            missing_creds.append('IBM_TRANSLATOR_API_KEY')
        if not os.getenv('IBM_WATSONX_API_KEY'):
            missing_creds.append('IBM_WATSONX_API_KEY')
        if not os.getenv('IBM_WATSONX_PROJECT_ID'):
            missing_creds.append('IBM_WATSONX_PROJECT_ID')
        
        if missing_creds:
            st.warning(f"⚠️ Missing API credentials: {', '.join(missing_creds)}. Some features may use fallback implementations.")
        
        st.session_state.api_status_checked = True
    
    def render_header(self):
        """Render the application header"""
        st.markdown('<h1 class="main-header">🎙️ EchoVerse</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Transform your text into expressive audiobooks with AI-powered rewriting and premium narration</p>', unsafe_allow_html=True)
        
        # Features overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**🎯 Tone-Adaptive**<br>Rewrite for any mood", unsafe_allow_html=True)
        with col2:
            st.markdown("**🎤 Premium Voices**<br>Human-like narration", unsafe_allow_html=True)
        with col3:
            st.markdown("**🌍 Multi-Language**<br>Translate & narrate", unsafe_allow_html=True)
        with col4:
            st.markdown("**📱 Easy Export**<br>Stream or download", unsafe_allow_html=True)
    
    def render_input_section(self):
        """Render the text input section"""
        st.header("📝 Input Your Content")
        
        # Input method selection with better styling
        col1, col2 = st.columns(2)
        with col1:
            input_method = st.radio(
                "Choose input method:",
                ["Type or paste text", "Upload .txt file"],
                horizontal=False
            )
        
        with col2:
            # Sample text buttons
            st.write("**Quick Start:**")
            if st.button("📖 Load Sample Story"):
                sample_text = """Once upon a time, in a quiet village nestled between rolling hills and whispering woods, there lived a young girl named Elena. She had always been curious about the world beyond her small home, dreaming of adventures that awaited in distant lands. Every evening, she would sit by her window and watch the stars, wondering what stories they might tell if only she could reach them.

One day, while exploring the forest near her village, Elena discovered an old, leather-bound book hidden beneath the roots of an ancient oak tree. As she opened the book, golden letters began to shimmer on the pages, and she realized this was no ordinary tome. It was a book of wishes, capable of bringing dreams to life.

With trembling hands, Elena wrote her deepest wish: to travel the world and help others find their own dreams. The moment she finished writing, the book glowed brightly, and a gentle wind lifted her off the ground. Her adventure was about to begin."""
                st.session_state.original_text = sample_text
                self._clear_dependent_states()
                st.rerun()
        
        if input_method == "Type or paste text":
            text_input = st.text_area(
                "Enter your text:",
                value=st.session_state.original_text,
                height=250,
                placeholder="Paste your story, article, or any text you want to convert to an audiobook...",
                help="Enter any text content you'd like to transform into an engaging audiobook"
            )
            if text_input != st.session_state.original_text:
                st.session_state.original_text = text_input
                self._clear_dependent_states()
        
        else:
            uploaded_file = st.file_uploader(
                "Upload a .txt file:",
                type=['txt'],
                help="Upload a plain text file to convert to audiobook"
            )
            if uploaded_file is not None:
                try:
                    text_content = uploaded_file.read().decode('utf-8')
                    if text_content != st.session_state.original_text:
                        st.session_state.original_text = text_content
                        self._clear_dependent_states()
                    st.success(f"✅ Loaded {len(text_content)} characters from {uploaded_file.name}")
                except UnicodeDecodeError:
                    st.error("❌ Could not decode file. Please ensure it's a valid UTF-8 text file.")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        # Text validation and stats
        if st.session_state.original_text:
            validation = self.text_service.validate_text_input(st.session_state.original_text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", validation['stats']['word_count'])
            with col2:
                st.metric("Characters", validation['stats']['character_count'])
            with col3:
                st.metric("Est. Audio Duration", f"{validation['stats']['estimated_audio_duration_minutes']:.1f} min")
            
            if not validation['valid']:
                for issue in validation['issues']:
                    st.warning(f"⚠️ {issue}")
            
            if validation['recommendations']:
                with st.expander("💡 Recommendations"):
                    for rec in validation['recommendations']:
                        st.info(rec)
    
    def _clear_dependent_states(self):
        """Clear states that depend on the input text"""
        st.session_state.rewritten_text = ""
        st.session_state.translated_text = ""
        st.session_state.audio_data = None
        st.session_state.translated_audio_data = None
        st.session_state.processing_status = ""
    
    def render_tone_selection(self):
        """Render tone selection and rewriting controls"""
        st.header("🎭 Tone-Adaptive Rewriting")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_tone = st.selectbox(
                "Choose writing tone:",
                ["Neutral", "Suspenseful", "Inspiring"],
                index=["Neutral", "Suspenseful", "Inspiring"].index(st.session_state.selected_tone),
                help="Select the emotional tone for AI rewriting"
            )
            st.session_state.selected_tone = selected_tone
            
            # Tone descriptions with examples
            tone_descriptions = {
                "Neutral": {
                    "desc": "📖 Clear, balanced, and professional tone suitable for informational content",
                    "example": "The character walked through the forest and found an interesting object."
                },
                "Suspenseful": {
                    "desc": "🔍 Mysterious, tension-building tone perfect for thrillers and mysteries", 
                    "example": "The character crept through the shadowy forest and discovered something unsettling."
                },
                "Inspiring": {
                    "desc": "✨ Uplifting, motivational tone that energizes and encourages readers",
                    "example": "The character journeyed through the majestic forest and discovered their true potential."
                }
            }
            
            st.markdown(f"*{tone_descriptions[selected_tone]['desc']}*")
            with st.expander("📝 See example transformation"):
                st.write(f"**{selected_tone} style:** {tone_descriptions[selected_tone]['example']}")
        
        with col2:
            # Check for rate limiting
            can_rewrite = True
            if st.session_state.last_rewrite_time > 0:
                time_since_last = time.time() - st.session_state.last_rewrite_time
                if time_since_last < 5:  # 5 second cooldown
                    can_rewrite = False
                    st.info(f"⏱️ Wait {5-int(time_since_last)}s")
            
            if st.button("🔄 Rewrite Text", type="primary", 
                        disabled=not st.session_state.original_text or not can_rewrite):
                st.session_state.processing_status = "rewriting"
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🤖 Analyzing text...")
                    progress_bar.progress(25)
                    
                    status_text.text(f"🎭 Applying {selected_tone.lower()} tone...")
                    progress_bar.progress(50)
                    
                    rewritten_text = self.text_service.rewrite_with_tone(
                        st.session_state.original_text,
                        selected_tone
                    )
                    
                    progress_bar.progress(75)
                    status_text.text("✨ Finalizing rewrite...")
                    
                    st.session_state.rewritten_text = rewritten_text
                    st.session_state.last_rewrite_time = time.time()
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Rewriting complete!")
                    
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error rewriting text: {str(e)}")
                    logger.error(f"Rewriting error: {e}")
                finally:
                    st.session_state.processing_status = ""
        
        with col3:
            if st.session_state.rewritten_text:
                # Show rewrite stats
                original_words = len(st.session_state.original_text.split())
                rewritten_words = len(st.session_state.rewritten_text.split())
                change_pct = ((rewritten_words - original_words) / original_words * 100) if original_words > 0 else 0
                
                st.metric(
                    "Word Change", 
                    f"{change_pct:+.0f}%",
                    delta=f"{rewritten_words - original_words} words"
                )
    
    def render_text_comparison(self):
        """Render side-by-side text comparison"""
        if st.session_state.original_text or st.session_state.rewritten_text or st.session_state.translated_text:
            st.header("📊 Text Comparison")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📄 Original")
                if st.session_state.original_text:
                    st.markdown(f'<div class="text-panel">{st.session_state.original_text[:500]}{"..." if len(st.session_state.original_text) > 500 else ""}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.info("No original text yet")
            
            with col2:
                st.subheader(f"🎭 Rewritten ({st.session_state.selected_tone})")
                if st.session_state.rewritten_text:
                    st.markdown(f'<div class="text-panel">{st.session_state.rewritten_text[:500]}{"..." if len(st.session_state.rewritten_text) > 500 else ""}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.info("Click 'Rewrite Text' to see AI-enhanced version")
            
            with col3:
                st.subheader(f"🌍 Translated ({st.session_state.target_language})")
                if st.session_state.translated_text:
                    st.markdown(f'<div class="text-panel">{st.session_state.translated_text[:500]}{"..." if len(st.session_state.translated_text) > 500 else ""}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.info("Select language and translate to see result")
    
    def render_voice_controls(self):
        """Render voice selection and audio generation controls"""
        st.header("🎤 Voice & Audio Generation")
        
        # Advanced options toggle
        if st.checkbox("🔧 Show Advanced Audio Options", value=st.session_state.show_advanced_options):
            st.session_state.show_advanced_options = True
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.speech_speed = st.slider(
                    "Speech Speed", 0.5, 2.0, st.session_state.speech_speed, 0.1
                )
            with col2:
                st.session_state.audio_quality = st.selectbox(
                    "Audio Quality", ["Standard", "High", "Premium"], 
                    index=["Standard", "High", "Premium"].index(st.session_state.audio_quality)
                )
        else:
            st.session_state.show_advanced_options = False
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_voice = st.selectbox(
                "Choose narrator voice:",
                ["Lisa", "Michael", "Allison", "Kevin", "Emma", "Sophia", "Olivia", "Ava"],
                index=min(["Lisa", "Michael", "Allison", "Kevin", "Emma", "Sophia", "Olivia", "Ava"].index(st.session_state.selected_voice), 7),
                help="Select a premium, human-like voice for narration"
            )
            st.session_state.selected_voice = selected_voice
            
            # Voice descriptions with audio samples info
            voice_descriptions = {
                "Lisa": "🔊 Female, warm and expressive - Perfect for storytelling",
                "Michael": "🔊 Male, deep and authoritative - Great for dramatic content", 
                "Allison": "🔊 Female, crisp and professional - Ideal for informational content",
                "Kevin": "🔊 Male, friendly and conversational - Excellent for casual narratives",
                "Emma": "🔊 Female, young and energetic - Best for upbeat, inspiring content",
                "Sophia": "🔊 Female, clear and articulate - Excellent for educational content",
                "Olivia": "🔊 Female, soothing and calm - Perfect for meditation and relaxation",
                "Ava": "🔊 Female, vibrant and dynamic - Great for engaging narratives"
            }
            st.markdown(f"*{voice_descriptions[selected_voice]}*")
            
            # Voice sample player (if available)
            if st.button(f"🎧 Preview {selected_voice}"):
                sample_text = f"Hello! I'm {selected_voice}. I'll bring your stories to life with emotion and clarity."
                try:
                    sample_audio = self.audio_service.generate_speech(
                        sample_text, voice=selected_voice, language="en"
                    )
                    if sample_audio:
                        st.audio(sample_audio, format='audio/mp3')
                except Exception as e:
                    st.error(f"Could not generate voice preview: {e}")
        
        with col2:
            # Validate text before generation
            text_validation = None
            if st.session_state.rewritten_text:
                text_validation = self.audio_service.validate_text_for_speech(st.session_state.rewritten_text)
                if not text_validation['valid']:
                    for issue in text_validation['issues']:
                        st.warning(f"⚠️ {issue}")
            
            # Generate button with better status handling
            can_generate = (st.session_state.rewritten_text and 
                          (not text_validation or text_validation['valid']))
            
            if st.button("🎵 Generate Audio", type="primary", disabled=not can_generate):
                st.session_state.processing_status = "generating_audio"
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🎙️ Initializing voice synthesis...")
                    progress_bar.progress(20)
                    
                    status_text.text(f"🎤 Using {selected_voice} voice...")
                    progress_bar.progress(40)
                    
                    audio_data = self.audio_service.generate_speech(
                        st.session_state.rewritten_text,
                        voice=selected_voice,
                        language="en"
                    )
                    
                    progress_bar.progress(80)
                    status_text.text("🔧 Processing audio...")
                    
                    if audio_data:
                        st.session_state.audio_data = audio_data
                        progress_bar.progress(100)
                        status_text.text("✅ Audio generation complete!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ No audio data generated")
                        
                except Exception as e:
                    st.error(f"❌ Error generating audio: {str(e)}")
                    logger.error(f"Audio generation error: {e}")
                finally:
                    st.session_state.processing_status = ""
        
        with col3:
            # Audio playback and download
            if st.session_state.audio_data:
                st.subheader("🎧 Generated Audio")
                st.audio(st.session_state.audio_data, format='audio/mp3')
                
                # Audio info
                audio_info = self.audio_service.get_audio_info(st.session_state.audio_data)
                if audio_info:
                    st.caption(f"Size: {audio_info.get('size_kb', 0)} KB | Duration: ~{audio_info.get('estimated_duration_seconds', 0):.0f}s")
                
                # Download button with better filename
                timestamp = int(time.time())
                filename = f"echoverse_{st.session_state.selected_tone.lower()}_{st.session_state.selected_voice.lower()}_{timestamp}.mp3"
                
                st.download_button(
                    label="📥 Download MP3",
                    data=st.session_state.audio_data,
                    file_name=filename,
                    mime="audio/mp3",
                    help="Download the generated audiobook as MP3 file"
                )
                
                # Share options
                if st.button("🔗 Copy Audio Link"):
                    st.info("💡 Audio is generated locally. Use the download button to save the file.")
    
    def render_translation_section(self):
        """Render translation and multilingual audio section"""
        st.header("🌍 Translation & Multilingual Audio")
        
        # Language support info
        st.info("🌐 **Multi-Language Support:** Translate your audiobook into multiple languages with native voice narration!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Enhanced language selection with flags and descriptions
            language_options = {
                "Spanish": "🇪🇸 Spanish (Español)",
                "French": "🇫🇷 French (Français)",
                "German": "🇩🇪 German (Deutsch)",
                "Italian": "🇮🇹 Italian (Italiano)",
                "Portuguese": "🇵🇹 Portuguese (Português)",
                "Hindi": "🇮🇳 Hindi (हिन्दी)",
                "Chinese": "🇨🇳 Chinese (中文)",
                "Japanese": "🇯🇵 Japanese (日本語)",
                "Tamil": "🇮🇳 Tamil (தமிழ்)",
                "English": "🇺🇸 English"
            }
            
            target_language = st.selectbox(
                "Target language:",
                list(language_options.keys()),
                index=list(language_options.keys()).index(st.session_state.target_language),
                format_func=lambda x: language_options[x],
                help="Choose language for translation and voice synthesis"
            )
            st.session_state.target_language = target_language
            
            # Language info
            lang_info = {
                "Spanish": "Most widely spoken Romance language",
                "French": "Language of diplomacy and culture", 
                "German": "Major European business language",
                "Italian": "Language of art and music",
                "Portuguese": "Spoken in Brazil and Portugal",
                "Hindi": "One of India's official languages",
                "Chinese": "Most spoken language in the world",
                "Japanese": "Language of technology and anime",
                "Tamil": "One of the oldest living languages in the world",
                "English": "Global language of business and science"
            }
            st.caption(lang_info.get(target_language, ""))
        
        with col2:
            # Rate limiting for translation
            can_translate = True
            if st.session_state.last_translation_time > 0:
                time_since_last = time.time() - st.session_state.last_translation_time
                if time_since_last < 10:  # 10 second cooldown for translation
                    can_translate = False
                    st.info(f"⏱️ Wait {10-int(time_since_last)}s")
            
            if st.button("🔄 Translate", type="primary", 
                        disabled=not st.session_state.rewritten_text or not can_translate):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🌐 Connecting to translation service...")
                    progress_bar.progress(25)
                    
                    status_text.text(f"🔄 Translating to {target_language}...")
                    progress_bar.progress(50)
                    
                    translated_text = self.watson_service.translate_text(
                        st.session_state.rewritten_text,
                        target_language=self._get_language_code(target_language)
                    )
                    
                    progress_bar.progress(75)
                    status_text.text("✨ Finalizing translation...")
                    
                    if translated_text:
                        st.session_state.translated_text = translated_text
                        st.session_state.last_translation_time = time.time()
                        
                        progress_bar.progress(100)
                        status_text.text(f"✅ Translated to {target_language}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Translation returned empty result")
                        
                except Exception as e:
                    st.error(f"❌ Translation error: {str(e)}")
                    logger.error(f"Translation error: {e}")
        
        with col3:
            # Check if selected language has limited support
            language_code = self._get_language_code(target_language)
            is_limited_support = target_language in self.limited_support_languages
            
            if is_limited_support:
                st.warning(f"⚠️ {target_language} has limited system voice support which may result in poor audio quality. Consider using cloud-based TTS services for better results.")
            
            if st.button("🎵 Generate Translated Audio", disabled=not st.session_state.translated_text):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🎙️ Initializing multilingual TTS...")
                    progress_bar.progress(25)
                    
                    status_text.text(f"🎤 Creating {target_language} narration...")
                    progress_bar.progress(50)
                    
                    # Get language code for the target language
                    language_code = self._get_language_code(target_language)
                    logger.info(f"Generating audio for {target_language} with language code: {language_code}")
                    
                    translated_audio = self.audio_service.generate_speech(
                        st.session_state.translated_text,
                        voice=st.session_state.selected_voice,
                        language=language_code  # This is the key fix - pass the language code!
                    )
                    
                    progress_bar.progress(75)
                    status_text.text("🔧 Processing multilingual audio...")
                    
                    if translated_audio:
                        # Check if the generated audio is unusually small
                        if translated_audio and isinstance(translated_audio, bytes) and len(translated_audio) < 100 and len(st.session_state.translated_text) > 50:
                            st.warning("⚠️ The generated audio is unusually small, which may indicate that your system doesn't have proper voice support for this language. The audio may not sound correct.")
                            logger.warning(f"Generated audio is unusually small ({len(translated_audio)} bytes) for {target_language} text of length {len(st.session_state.translated_text)}")
                        
                        st.session_state.translated_audio_data = translated_audio
                        progress_bar.progress(100)
                        status_text.text(f"✅ {target_language} audio generated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Handle case where no audio was generated
                        if is_limited_support:
                            st.error(f"❌ No {target_language} audio could be generated. This language has limited system support. Consider installing language-specific voice packages or using cloud-based TTS services.")
                        else:
                            st.error(f"❌ No {target_language} audio generated")
                        
                except Exception as e:
                    st.error(f"❌ Error generating {target_language} audio: {str(e)}")
                    logger.error(f"Translated audio generation error: {e}")
        
        # Enhanced multilingual audio section
        if st.session_state.translated_text or st.session_state.translated_audio_data:
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.session_state.translated_text:
                    st.subheader(f"📝 {st.session_state.target_language} Text")
                    with st.expander(f"View {st.session_state.target_language} translation", expanded=True):
                        st.text_area(f"{st.session_state.target_language} translation", 
                                   value=st.session_state.translated_text,
                                   height=200,
                                   key="translated_text_display",
                                   help="Full translated text")
                        
                        # Translation stats
                        orig_words = len(st.session_state.rewritten_text.split())
                        trans_words = len(st.session_state.translated_text.split())
                        st.caption(f"Translation: {orig_words} → {trans_words} words")
            
            with col2:
                if st.session_state.translated_audio_data:
                    st.subheader(f"🎧 {st.session_state.target_language} Audio")
                    
                    # Display audio player
                    st.audio(st.session_state.translated_audio_data, format='audio/mp3')
                    
                    # Audio information with enhanced details
                    audio_info = self.audio_service.get_audio_info(st.session_state.translated_audio_data)
                    if audio_info:
                        st.markdown(f"**Audio Details:**")
                        st.markdown(f"- **Size:** {audio_info.get('size_kb', 0)} KB")
                        st.markdown(f"- **Duration:** ~{audio_info.get('estimated_duration_seconds', 0):.0f} seconds")
                        st.markdown(f"- **Format:** {audio_info.get('format', 'MP3')}")
                        st.markdown(f"- **Language:** {st.session_state.target_language}")
                        st.markdown(f"- **Voice:** {st.session_state.selected_voice}")
                        st.markdown(f"- **Tone:** {st.session_state.selected_tone}")
                        
                        # Add warning if audio is unusually small
                        if (st.session_state.translated_audio_data and 
                            isinstance(st.session_state.translated_audio_data, bytes) and
                            audio_info.get('size_bytes', 0) < 100 and 
                            len(st.session_state.translated_text) > 50):
                            st.warning("⚠️ The generated audio is unusually small. Your system may not have proper voice support for this language.")
                    
                    # Enhanced download with timestamp
                    timestamp = int(time.time())
                    translated_filename = f"echoverse_{st.session_state.target_language.lower()}_{st.session_state.selected_tone.lower()}_{timestamp}.mp3"
                    
                    st.download_button(
                        label=f"📥 Download {st.session_state.target_language} MP3",
                        data=st.session_state.translated_audio_data,
                        file_name=translated_filename,
                        mime="audio/mp3",
                        help=f"Download the {st.session_state.target_language} audiobook"
                    )
                    
                    # Audio comparison
                    if st.session_state.audio_data:
                        st.info("🌐 **Compare:** Play both English and translated versions to hear the difference!")
                elif st.session_state.translated_text and not st.session_state.translated_audio_data:
                    st.info("📝 Translated text is ready. Click 'Generate Translated Audio' to create the audio version.")
    
    def render_sidebar(self):
        """Render enhanced sidebar with app info and settings"""
        st.sidebar.header("ℹ️ About EchoVerse")
        st.sidebar.markdown("""
        **EchoVerse** is an AI-powered audiobook creation tool that:
        
        • 🎭 **Rewrites** your text with different emotional tones
        • 🎤 **Narrates** with premium, human-like voices  
        • 🌍 **Translates** to multiple languages
        • 📱 **Exports** high-quality audio files
        
        **Powered by IBM Watson AI**
        """)
        
        # API Status indicator - Hidden as requested
        # st.sidebar.header("🔌 API Status")
        # api_status = self._check_api_status()
        # for service, status in api_status.items():
        #     if status:
        #         st.sidebar.success(f"✅ {service}")
        #     else:
        #         st.sidebar.error(f"❌ {service}")
        
        st.sidebar.header("⚙️ Settings")
        
        # Enhanced settings with persistence
        st.session_state.audio_quality = st.sidebar.selectbox(
            "Audio Quality:",
            ["Standard", "High", "Premium"],
            index=["Standard", "High", "Premium"].index(st.session_state.audio_quality)
        )
        
        st.session_state.speech_speed = st.sidebar.slider(
            "Speech Speed:",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.speech_speed,
            step=0.1,
            help="Adjust the narration speed"
        )
        
        # Export settings
        st.sidebar.subheader("📥 Export Options")
        export_format = st.sidebar.selectbox(
            "Audio Format:", ["MP3", "WAV"], index=0
        )
        
        batch_download = st.sidebar.checkbox(
            "Batch Download", 
            help="Download all generated audio files at once"
        )
        
        if batch_download and (st.session_state.audio_data or st.session_state.translated_audio_data):
            if st.sidebar.button("📦 Download All Audio"):
                self._create_batch_download()
        
        # Statistics and analytics
        st.sidebar.header("📊 Usage Stats")
        if st.session_state.original_text:
            stats = self.text_service.analyze_text_stats(st.session_state.original_text)
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("Words", stats['word_count'])
                st.metric("Sentences", stats['sentence_count'])
            with col2:
                st.metric("Est. Duration", f"{stats['estimated_audio_duration_minutes']:.1f}m")
                st.metric("Reading Time", f"{stats['estimated_reading_time_minutes']:.1f}m")
            
            # Progress indicator
            progress = 0
            if st.session_state.rewritten_text: progress += 33
            if st.session_state.audio_data: progress += 33
            if st.session_state.translated_text: progress += 34
            
            st.sidebar.progress(progress)
            st.sidebar.caption(f"Completion: {progress}%")
        
        # Help and feedback
        st.sidebar.header("🆘 Help & Support")
        with st.sidebar.expander("📝 Quick Guide"):
            st.markdown("""
            **Getting Started:**
            1. 📝 Input or upload your text
            2. 🎭 Choose a tone and rewrite
            3. 🎤 Select voice and generate audio
            4. 🌍 (Optional) Translate & create multilingual audio
            5. 📥 Download your audiobook!
            """)
        
        if st.sidebar.button("🐛 Report Issue"):
            st.sidebar.info("📧 Send feedback to: support@echoverse.ai")
    
    def _check_api_status(self) -> Dict[str, bool]:
        """Check API service availability"""
        return {
            "Watson TTS": bool(os.getenv('IBM_TTS_API_KEY')),
            "Watson Translator": bool(os.getenv('IBM_TRANSLATOR_API_KEY')),
            "Watsonx LLM": bool(os.getenv('IBM_WATSONX_API_KEY'))
        }
    
    def _create_batch_download(self):
        """Create a batch download of all audio files"""
        # This would create a ZIP file with all generated audio
        # Implementation would depend on specific requirements
        st.sidebar.success("📦 Batch download feature coming soon!")
    
    def _get_language_code(self, language_name: str) -> str:
        """Convert language name to code"""
        language_codes = {
            "Spanish": "es",
            "French": "fr", 
            "German": "de",
            "Italian": "it",
            "Portuguese": "pt",
            "Hindi": "hi",
            "Chinese": "zh",
            "Japanese": "ja",
            "Tamil": "ta",
            "English": "en",
            "Korean": "ko",
            "Russian": "ru",
            "Arabic": "ar",
            "Dutch": "nl",
            "Swedish": "sv",
            "Polish": "pl",
            "Turkish": "tr",
            "Thai": "th",
            "Vietnamese": "vi"
        }
        return language_codes.get(language_name, "en")
    
    def run(self):
        """Run the main application with enhanced flow"""
        try:
            self.render_header()
            
            # Check for processing status
            if st.session_state.processing_status:
                st.info(f"🔄 Processing: {st.session_state.processing_status}...")
            
            # Main content area with improved flow
            self.render_input_section()
            
            if st.session_state.original_text:
                self.render_tone_selection()
                self.render_text_comparison()
                
                if st.session_state.rewritten_text:
                    self.render_voice_controls()
                    self.render_translation_section()
                    
                    # Show completion status
                    if st.session_state.audio_data and st.session_state.translated_audio_data:
                        st.success("🎉 **Congratulations!** Your multilingual audiobook is complete!")
                        
                        # Final summary
                        with st.expander("📋 Project Summary", expanded=True):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Tone", st.session_state.selected_tone)
                            with col2:
                                st.metric("Voice", st.session_state.selected_voice)
                            with col3:
                                st.metric("Languages", f"English + {st.session_state.target_language}")
                    
                    elif st.session_state.audio_data:
                        st.info("🎆 **Almost done!** You can now translate to create a multilingual audiobook.")
            
            # Sidebar
            self.render_sidebar()
            
            # Footer
            st.markdown("---")
            st.markdown("🌟 **EchoVerse** - Transform your words into captivating audiobooks with AI", 
                       help="Built with Streamlit and IBM Watson AI")
            
        except Exception as e:
            st.error(f"❌ Application error: {str(e)}")
            logger.error(f"Application error: {e}")
            
            # Error recovery options
            if st.button("🔄 Reset Application"):
                for key in list(st.session_state.keys()):
                    if isinstance(key, str) and key.startswith(('original_', 'rewritten_', 'translated_', 'audio_', 'processing_')):
                        del st.session_state[key]
                st.rerun()

def main():
    """Main entry point with error handling"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        app = EchoVerseApp()
        app.run()
        
    except ImportError:
        # dotenv not available, continue without it
        app = EchoVerseApp()
        app.run()
    except Exception as e:
        st.error(f"🚫 Critical error starting EchoVerse: {e}")
        st.markdown("""
        **Troubleshooting:**
        1. Ensure all dependencies are installed: `pip install -r requirements_echoverse.txt`
        2. Check your .env file has valid IBM Watson credentials
        3. Restart the Streamlit app: `streamlit run echoverse_app.py`
        """)
        logger.critical(f"Critical startup error: {e}")

if __name__ == "__main__":
    main()