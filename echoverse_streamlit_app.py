import streamlit as st
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from deep_translator import GoogleTranslator
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- CONFIG ----------------
st.set_page_config(page_title="EchoVerse", page_icon="🎧", layout="wide")
st.title("🎧 EchoVerse – AI-Powered Audiobook Creation Tool")

# Watson Credentials (use environment variables or Streamlit secrets)
TTS_API_KEY = os.getenv('IBM_TTS_API_KEY') or st.secrets.get("IBM_TTS_API_KEY", "your-tts-api-key")
TTS_URL = os.getenv('IBM_TTS_URL') or st.secrets.get("IBM_TTS_URL", "https://api.us-south.text-to-speech.watson.cloud.ibm.com")

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize IBM Watson and Google Translator services"""
    tts_service = None
    translator_service = None
    
    # Setup TTS
    if TTS_API_KEY and TTS_API_KEY != "your-tts-api-key":
        try:
            tts_auth = IAMAuthenticator(TTS_API_KEY)
            tts_service = TextToSpeechV1(authenticator=tts_auth)
            tts_service.set_service_url(TTS_URL)
            logger.info("✅ IBM Text-to-Speech service initialized")
        except Exception as e:
            st.error(f"Failed to initialize TTS service: {e}")
    else:
        st.warning("⚠️ Please configure your IBM TTS API credentials")
    
    # Setup Google Translator (replaces deprecated IBM Language Translator)
    try:
        translator_service = GoogleTranslator(source='en', target='en')
        logger.info("✅ Google Translator service initialized")
    except Exception as e:
        st.error(f"Failed to initialize translator service: {e}")
    
    return tts_service, translator_service

def rewrite_text_with_tone(text: str, tone: str) -> str:
    """Simple rule-based text rewriting based on tone"""
    if tone == "Suspenseful":
        # Add suspenseful elements
        text = text.replace(" said ", " whispered ")
        text = text.replace(" went ", " crept ")
        text = text.replace(" walked ", " stalked ")
        if not text.endswith("..."):
            text += "... something stirred in the shadows."
    elif tone == "Inspiring":
        # Add inspiring elements
        text = text.replace(" said ", " declared ")
        text = text.replace(" tried ", " strived ")
        text = text.replace(" did ", " accomplished ")
        text += " This shows the power of determination and perseverance."
    
    return text

# Initialize services
tts_service, translator_service = initialize_services()

# ---------------- INPUT ----------------
uploaded_file = st.file_uploader("Upload a .txt file", type="txt")
user_text = st.text_area("Or paste your text here:", height=150)

if uploaded_file:
    try:
        user_text = uploaded_file.read().decode("utf-8")
        st.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")

if user_text:
    st.subheader("📝 Original Text")
    with st.expander("View original text", expanded=False):
        st.write(user_text)

    # Configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tone = st.radio("🎭 Choose a tone:", ["Neutral", "Suspenseful", "Inspiring"])
    
    with col2:
        voice = st.selectbox("🎤 Choose a voice:", [
            "en-US_AllisonV3Voice",
            "en-US_MichaelV3Voice", 
            "en-US_LisaV3Voice",
            "en-US_KevinV3Voice",
            "en-US_EmmaExpressive"
        ])
    
    with col3:
        target_lang = st.selectbox("🌍 Translate narration into:", [
            "None", 
            "es (Spanish)", 
            "fr (French)", 
            "de (German)",
            "it (Italian)",
            "pt (Portuguese)",
            "hi (Hindi)"
        ])

    if st.button("🚀 Rewrite, Translate & Generate Audio", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Rewrite using tone-based processing
            status_text.text("Step 1: Rewriting text with selected tone...")
            progress_bar.progress(25)
            
            rewritten_text = rewrite_text_with_tone(user_text, tone)
            
            # Step 2: Optional Translation
            translated_text = None
            if target_lang != "None" and translator_service:
                status_text.text("Step 2: Translating text...")
                progress_bar.progress(50)
                
                lang_code = target_lang.split()[0]  # e.g. "es"
                try:
                    # Create translator instance for specific language pair
                    translator = GoogleTranslator(source='en', target=lang_code)
                    translated_text = translator.translate(rewritten_text)
                    logger.info(f"Text translated to {lang_code}")
                except Exception as e:
                    st.error(f"Translation failed: {e}")
                    translated_text = rewritten_text
            
            # Step 3: Show Text Outputs
            status_text.text("Step 3: Displaying results...")
            progress_bar.progress(75)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**📄 Original Text**")
                st.text_area("", value=user_text[:500] + "..." if len(user_text) > 500 else user_text, 
                           height=200, disabled=True, key="original")
            
            with col2:
                st.markdown(f"**🎭 {tone} Rewrite**")
                st.text_area("", value=rewritten_text[:500] + "..." if len(rewritten_text) > 500 else rewritten_text,
                           height=200, disabled=True, key="rewritten")
            
            with col3:
                if translated_text:
                    st.markdown(f"**🌍 Translated Text ({target_lang})**")
                    st.text_area("", value=translated_text[:500] + "..." if len(translated_text) > 500 else translated_text,
                               height=200, disabled=True, key="translated")
                else:
                    st.markdown("**ℹ️ No Translation**")
                    st.info("Select a target language to enable translation")

            # Step 4: Convert to Speech
            if tts_service:
                status_text.text("Step 4: Generating audio...")
                progress_bar.progress(90)
                
                final_text = translated_text if translated_text else rewritten_text
                
                # Truncate text if too long (IBM TTS has limits)
                if len(final_text) > 5000:
                    final_text = final_text[:5000] + "..."
                    st.warning("Text was truncated to 5000 characters for audio generation")
                
                try:
                    # CORRECTED: Use proper IBM Watson SDK pattern
                    response = tts_service.synthesize(
                        text=final_text,
                        voice=voice,
                        accept="audio/mp3"
                    )
                    
                    # Get the audio content (bytes) from the response
                    audio_content = response.get_result()
                    
                    if audio_content and isinstance(audio_content, bytes):
                        # Save audio file
                        audio_file = "echoverse_output.mp3"
                        with open(audio_file, "wb") as f:
                            f.write(audio_content)
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Audio generation complete!")
                        
                        # Step 5: Play + Download
                        st.subheader("🎧 Generated Audio")
                        st.audio(audio_file, format="audio/mp3")
                        
                        with open(audio_file, "rb") as f:
                            st.download_button(
                                label="📥 Download Narration",
                                data=f.read(),
                                file_name="EchoVerse_Narration.mp3",
                                mime="audio/mp3"
                            )
                        
                        # Clean up temporary file
                        try:
                            os.remove(audio_file)
                        except:
                            pass
                            
                    else:
                        st.error("Failed to generate audio: No content received")
                        
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")
                    logger.error(f"TTS error: {e}")
            else:
                st.error("Text-to-Speech service not available. Please check your API credentials.")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            logger.error(f"Application error: {e}")
        finally:
            progress_bar.empty()
            status_text.empty()

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About EchoVerse")
    st.info("""
    EchoVerse transforms your text into engaging audiobooks with:
    
    - **Tone Rewriting**: Neutral, Suspenseful, or Inspiring
    - **Multi-language Translation**: Support for 7+ languages  
    - **Professional TTS**: IBM Watson voices
    - **Easy Download**: Get your audiobook as MP3
    """)
    
    st.header("🔧 Setup Instructions")
    st.markdown("""
    1. Get IBM Watson TTS API key from [IBM Cloud](https://cloud.ibm.com)
    2. Set environment variables:
       - `IBM_TTS_API_KEY`
       - `IBM_TTS_URL`
    3. Or use Streamlit secrets
    """)
    
    # Service status
    st.header("📊 Service Status")
    st.success("✅ Google Translator") if translator_service else st.error("❌ Google Translator")
    st.success("✅ IBM TTS") if tts_service else st.error("❌ IBM TTS")