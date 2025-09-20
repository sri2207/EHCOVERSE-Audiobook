import requests
import json
import time
import os

def test_complete_workflow():
    """Test the complete workflow from language selection to audio generation"""
    
    print("=== Testing Complete Audiobook Generation Workflow ===\n")
    
    # Step 1: Get available languages
    print("Step 1: Getting available languages...")
    response = requests.get('http://localhost:5000/get-languages')
    if response.status_code != 200:
        print(f"❌ Failed to get languages: {response.status_code}")
        return
    
    languages_data = response.json()
    print(f"✅ Successfully retrieved {len(languages_data['languages'])} languages")
    
    # Step 2: Test language detection
    print("\nStep 2: Testing language detection...")
    test_text = "This is a sample text for testing the language detection functionality."
    response = requests.post('http://localhost:5000/api/detect-language', 
                           json={'text': test_text})
    if response.status_code != 200:
        print(f"❌ Language detection failed: {response.status_code}")
        return
    
    detection_data = response.json()
    print(f"✅ Detected language: {detection_data['detected_language']} ({detection_data['language_name']})")
    print(f"   Confidence: {detection_data['confidence']}")
    
    # Step 3: Test translation to Spanish
    print("\nStep 3: Testing translation to Spanish...")
    response = requests.post('http://localhost:5000/api/translate',
                           json={
                               'text': test_text,
                               'target_language': 'es'
                           })
    if response.status_code != 200:
        print(f"❌ Translation failed: {response.status_code}")
        return
    
    translation_data = response.json()
    print(f"✅ Translation successful")
    print(f"   Original: {test_text[:50]}...")
    print(f"   Translated: {translation_data['translated_text'][:50]}...")
    print(f"   Source: {translation_data['source_language']} -> Target: {translation_data['target_language']}")
    
    # Step 4: Test audio generation with English text
    print("\nStep 4: Testing audio generation with English text...")
    audio_filename = f"test_english_{int(time.time())}.wav"
    response = requests.post('http://localhost:5000/api/generate-audio',
                           json={
                               'text': test_text,
                               'settings': {
                                   'rate': 175,
                                   'volume': 0.9,
                                   'voice_type': 'female_warm',
                                   'target_language': 'en'
                               }
                           })
    if response.status_code != 200:
        print(f"❌ English audio generation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    audio_data = response.json()
    print(f"✅ English audio generation successful")
    print(f"   Audio file: {audio_data['audio_file']}")
    
    # Step 5: Test audio generation with Spanish text
    print("\nStep 5: Testing audio generation with Spanish text...")
    audio_filename = f"test_spanish_{int(time.time())}.wav"
    response = requests.post('http://localhost:5000/api/generate-audio',
                           json={
                               'text': translation_data['translated_text'],
                               'settings': {
                                   'rate': 175,
                                   'volume': 0.9,
                                   'voice_type': 'female_warm',
                                   'target_language': 'es'
                               }
                           })
    if response.status_code != 200:
        print(f"❌ Spanish audio generation failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    audio_data = response.json()
    print(f"✅ Spanish audio generation successful")
    print(f"   Audio file: {audio_data['audio_file']}")
    
    # Step 6: Verify audio files were created
    print("\nStep 6: Verifying audio files...")
    audio_files = [f for f in os.listdir('audio_output') if f.endswith('.wav')]
    if audio_files:
        print(f"✅ Found {len(audio_files)} audio files in output directory")
        print("   Latest files:")
        for file in sorted(audio_files, reverse=True)[:3]:
            print(f"     - {file}")
    else:
        print("⚠️  No audio files found in output directory")
    
    print("\n=== Workflow Test Complete ===")
    print("✅ All steps completed successfully!")

if __name__ == "__main__":
    test_complete_workflow()