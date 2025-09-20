#!/usr/bin/env python3
"""
Test script to verify audio file access through Flask API
"""

import sys
import os
from pathlib import Path
import requests

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def test_audio_file_access():
    """Test accessing audio files through Flask API"""
    print("🔊 Testing Audio File Access Through Flask API")
    print("=" * 50)
    
    try:
        # Check if server is running
        try:
            response = requests.get("http://127.0.0.1:5000/", timeout=5)
            print("✅ Flask server is running")
        except requests.exceptions.ConnectionError:
            print("❌ Flask server is not running")
            print("   Please start the Flask server with: python app.py")
            return False
        except Exception as e:
            print(f"❌ Error connecting to Flask server: {e}")
            return False
        
        # Test accessing the files list endpoint
        print("\n1. Testing /files endpoint...")
        try:
            response = requests.get("http://127.0.0.1:5000/files", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Files endpoint accessible")
                # Check if we got HTML content
                if 'text/html' in response.headers.get('content-type', ''):
                    print("   ✅ Received HTML content as expected")
                else:
                    print(f"   ⚠️  Unexpected content type: {response.headers.get('content-type')}")
            else:
                print(f"   ❌ Files endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error accessing files endpoint: {e}")
        
        # Test accessing a specific audio file
        print("\n2. Testing audio file access...")
        
        # First, let's see what files are available
        audio_output_dir = Path(__file__).parent / "audio_output"
        if audio_output_dir.exists():
            wav_files = list(audio_output_dir.glob("*.wav"))
            print(f"   Found {len(wav_files)} WAV files in audio_output directory")
            
            if wav_files:
                # Try to access the first file through the API
                first_file = wav_files[0].name
                print(f"   Testing access to: {first_file}")
                
                try:
                    # Test the download endpoint
                    download_url = f"http://127.0.0.1:5000/api/download/{first_file}"
                    print(f"   Download URL: {download_url}")
                    
                    response = requests.get(download_url, timeout=10)
                    print(f"   Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ Audio file accessible through API")
                        content_type = response.headers.get('content-type', '')
                        print(f"   Content-Type: {content_type}")
                        
                        if 'audio' in content_type:
                            print("   ✅ Correct content type for audio")
                        else:
                            print(f"   ⚠️  Unexpected content type for audio: {content_type}")
                            
                        # Check file size
                        content_length = response.headers.get('content-length')
                        if content_length:
                            size_mb = int(content_length) / (1024 * 1024)
                            print(f"   File size: {size_mb:.2f} MB")
                    else:
                        print(f"   ❌ Audio file access failed with status {response.status_code}")
                        print(f"   Response: {response.text[:200]}...")
                except Exception as e:
                    print(f"   ❌ Error accessing audio file: {e}")
            else:
                print("   ⚠️  No WAV files found in audio_output directory")
        else:
            print("   ❌ audio_output directory not found")
            
        # Test the API status endpoint
        print("\n3. Testing API status endpoint...")
        try:
            response = requests.get("http://127.0.0.1:5000/api/status", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Response: {result}")
                    if result.get('application') == 'running':
                        print("   ✅ Application is running")
                    else:
                        print("   ⚠️  Application status unknown")
                except:
                    print("   ⚠️  Could not parse JSON response")
            else:
                print(f"   ❌ Status endpoint returned {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error accessing status endpoint: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audio_file_access()
    if success:
        print("\n🎉 Audio file access test completed!")
    else:
        print("\n💥 Audio file access test failed!")