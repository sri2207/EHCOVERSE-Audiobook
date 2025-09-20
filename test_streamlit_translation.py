import streamlit as st
from deep_translator import GoogleTranslator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_streamlit_translation():
    """Test translation functionality in Streamlit context"""
    st.title("Translation Test")
    
    # Test text
    text = "Hello, how are you today? This is a test of the translation system."
    st.write(f"Original text: {text}")
    
    # Test translation to Spanish
    try:
        # Create translator instance for specific language pair
        translator = GoogleTranslator(source='en', target='es')
        translated_text = translator.translate(text)
        st.write(f"Translated to Spanish: {translated_text}")
        st.success("✅ Translation test PASSED")
        logger.info("Translation test passed successfully")
        return True
    except Exception as e:
        st.error(f"❌ Translation test FAILED: {e}")
        logger.error(f"Translation test failed: {e}")
        return False

if __name__ == "__main__":
    test_streamlit_translation()