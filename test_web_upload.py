#!/usr/bin/env python3
"""
Test the web upload functionality directly
"""

import sys
import requests
import os
from pathlib import Path

def test_web_upload():
    """Test uploading a file to the web interface"""
    try:
        print("🌐 Testing Web Upload Functionality")
        print("=" * 40)
        
        # Test file
        test_file = "sample_docs/sample_text.txt"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file {test_file} not found")
            return
            
        print(f"📄 Uploading file: {test_file}")
        
        # Upload to the Flask app
        url = "http://localhost:5000/upload"
        
        # Prepare the file for upload
        with open(test_file, 'rb') as f:
            files = {'file': (os.path.basename(test_file), f, 'text/plain')}
            data = {
                'voice_type': 'female_warm',
                'voice_rate': '175',
                'voice_volume': '0.9',
                'enable_naturalness': 'true',
                'continuous_flow': 'true',
                'enable_ai_features': 'true'
            }
            
            print("📤 Sending upload request...")
            response = requests.post(url, files=files, data=data)
            
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Audio file: {result.get('audio_file', 'N/A')}")
            if 'text_preview' in result:
                print(f"   Text preview: {result['text_preview'][:100]}...")
        else:
            print(f"❌ Upload failed!")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to the Flask server")
        print("   Make sure the Flask app is running on port 5000")
        print("   Start it with: python app.py")
    except Exception as e:
        print(f"❌ Error testing web upload: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_web_upload()