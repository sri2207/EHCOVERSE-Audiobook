#!/usr/bin/env python3
"""
Test script to verify audio display improvements
"""

import streamlit as st
import time

# Initialize session state
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = "This is a sample translated text in Tamil. இது தமிழில் மொழிபெயர்க்கப்பட்ட உரையின் எடுத்துக்காட்டு ஆகும்."

if 'translated_audio_data' not in st.session_state:
    st.session_state.translated_audio_data = b"fake_audio_data_for_testing"

if 'target_language' not in st.session_state:
    st.session_state.target_language = "Tamil"

if 'selected_voice' not in st.session_state:
    st.session_state.selected_voice = "Lisa"

if 'selected_tone' not in st.session_state:
    st.session_state.selected_tone = "Neutral"

st.title("Audio Display Test")

# Test the improved audio display section
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📝 {st.session_state.target_language} Text")
    with st.expander(f"View {st.session_state.target_language} translation", expanded=True):
        st.text_area(f"{st.session_state.target_language} translation", 
                   value=st.session_state.translated_text,
                   height=200,
                   key="translated_text_display",
                   help="Full translated text")

with col2:
    if st.session_state.translated_audio_data:
        st.subheader(f"🎧 {st.session_state.target_language} Audio")
        
        # Display audio player
        st.audio(st.session_state.translated_audio_data, format='audio/mp3')
        
        # Audio information with enhanced details
        st.markdown(f"**Audio Details:**")
        st.markdown(f"- **Size:** 0.05 KB")
        st.markdown(f"- **Duration:** ~30 seconds")
        st.markdown(f"- **Format:** MP3")
        st.markdown(f"- **Language:** {st.session_state.target_language}")
        st.markdown(f"- **Voice:** {st.session_state.selected_voice}")
        st.markdown(f"- **Tone:** {st.session_state.selected_tone}")
        
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
        st.info("🌐 **Compare:** Play both English and translated versions to hear the difference!")
    elif st.session_state.translated_text and not st.session_state.translated_audio_data:
        st.info("📝 Translated text is ready. Click 'Generate Translated Audio' to create the audio version.")