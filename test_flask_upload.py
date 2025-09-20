#!/usr/bin/env python3
"""
Test the Flask upload endpoint directly
"""

import sys
import os
from pathlib import Path
import requests

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def test_flask_upload():
    """Test the Flask upload endpoint directly"""
    print("🌐 Testing Flask Upload Endpoint")
    print("=" * 40)
    
    try:
        # Create test content
        test_content = """
        This is a test of the EchoVerse Flask upload endpoint.
        If this test works, then the web interface should also work.
        """
        
        # Create a test text file
        project_root = Path(__file__).parent
        static_dir = project_root / "static"
        uploads_dir = static_dir / "uploads"
        
        # Ensure directories exist
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test file
        test_file_path = uploads_dir / "test_flask.txt"
        test_file_path.write_text(test_content, encoding='utf-8')
        print(f"✅ Created test file: {test_file_path}")
        
        # Test Flask upload endpoint
        url = "http://127.0.0.1:5000/upload"
        print(f"\n1. Testing upload to: {url}")
        
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
        
        # Prepare file for upload
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path.name, f, 'text/plain')}
            data = {
                'voice_rate': '175',
                'voice_volume': '0.9',
                'voice_type': 'female_warm',
                'target_language': 'en',
                'enable_naturalness': 'true',
                'continuous_flow': 'true',
                'enable_ai_features': 'true',
                'enable_translation': 'true'
            }
            
            print("\n2. Sending upload request...")
            response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"3. Response Status: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response JSON: {result}")
                if result.get('success'):
                    print("✅ Upload endpoint working correctly!")
                    audio_file = result.get('audio_file')
                    if audio_file:
                        # Check the correct audio output directory
                        audio_path = Path(__file__).parent / "audio_output" / audio_file
                        if audio_path.exists():
                            print(f"   Audio file generated: {audio_path}")
                            print(f"   File size: {audio_path.stat().st_size} bytes")
                        else:
                            print(f"   ⚠️  Audio file not found at expected location: {audio_path}")
                            # List files in audio_output to see what's there
                            audio_output_dir = Path(__file__).parent / "audio_output"
                            if audio_output_dir.exists():
                                files = list(audio_output_dir.iterdir())
                                print(f"   Files in audio_output directory: {len(files)}")
                                # Show last few files
                                for f in files[-3:]:
                                    print(f"     - {f.name}")
                    return True
                else:
                    print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                    return False
            except Exception as e:
                print(f"   Response Text: {response.text}")
                print(f"   Error parsing JSON: {e}")
                return False
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"   Response Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_flask_upload()
    if success:
        print("\n🎉 Flask upload endpoint is working correctly!")
    else:
        print("\n💥 Flask upload endpoint has issues!")