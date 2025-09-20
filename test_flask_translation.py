import requests
import json

def test_flask_translation():
    """Test the Flask translation endpoint"""
    url = "http://localhost:5000/translate"
    
    # Test data
    data = {
        "text": "Hello, how are you today? This is a test of the translation system.",
        "target_language": "es"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Testing Flask translation endpoint...")
        response = requests.post(url, data=json.dumps(data), headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {response.status_code}")
            print(f"Success: {result.get('success', False)}")
            print(f"Translated text: {result.get('translated_text', 'N/A')}")
            print(f"Source language: {result.get('source_language', 'N/A')}")
            print(f"Target language: {result.get('target_language', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print("✅ Flask translation endpoint test PASSED")
            return True
        else:
            print(f"❌ Flask translation endpoint test FAILED with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Flask translation endpoint test FAILED with exception: {e}")
        return False

if __name__ == "__main__":
    test_flask_translation()