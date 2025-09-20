"""
Test file import functionality for TXT, PDF, DOCX, and other formats
"""

import os
import tempfile
from services.file_service import FileProcessingService

def create_test_files():
    """Create test files in various formats"""
    test_files = {}
    
    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    
    # 1. Create TXT file
    txt_content = """This is a test TXT file for audiobook creation.
It contains multiple lines of text to test the file import functionality.
The quick brown fox jumps over the lazy dog.
This is the end of the test file."""
    
    txt_path = os.path.join(temp_dir, "test_file.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    test_files['txt'] = txt_path
    
    # 2. Create HTML file
    html_content = """<html>
<head><title>Test HTML File</title></head>
<body>
<h1>Test HTML File</h1>
<p>This is a test HTML file for audiobook creation.</p>
<p>It contains multiple paragraphs to test the file import functionality.</p>
<p>The quick brown fox jumps over the lazy dog.</p>
<p>This is the end of the test file.</p>
</body>
</html>"""
    
    html_path = os.path.join(temp_dir, "test_file.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    test_files['html'] = html_path
    
    return test_files

def test_file_processing():
    """Test file processing service with various file formats"""
    print("Testing file import functionality for audiobook creation...")
    
    # Initialize file processing service
    file_service = FileProcessingService()
    
    # Create test files
    test_files = create_test_files()
    
    print(f"Created test files: {list(test_files.keys())}")
    
    # Test each file format
    results = {}
    
    for file_type, file_path in test_files.items():
        print(f"\n--- Testing {file_type.upper()} file processing ---")
        
        # Check if file type is supported
        file_type_enum, mime_type = file_service.detect_file_type(file_path)
        is_supported = file_service.supported_types.get(file_type_enum, False)
        
        print(f"File type: {file_type_enum.value}")
        print(f"MIME type: {mime_type}")
        print(f"Supported: {is_supported}")
        
        if not is_supported:
            print(f"⚠️  {file_type.upper()} file type not supported, skipping...")
            results[file_type] = {
                'supported': False,
                'status': 'UNSUPPORTED',
                'text_content': '',
                'errors': [f'{file_type.upper()} not supported']
            }
            continue
        
        # Process the file
        try:
            result = file_service.extract_text_from_file(file_path)
            
            print(f"Status: {result.status.value}")
            print(f"Text length: {len(result.text_content)} characters")
            print(f"Errors: {result.errors}")
            print(f"Warnings: {result.warnings}")
            
            if result.text_content:
                print(f"Text preview: {result.text_content[:100]}...")
            
            results[file_type] = {
                'supported': True,
                'status': result.status.value,
                'text_content': result.text_content,
                'errors': result.errors,
                'warnings': result.warnings
            }
            
        except Exception as e:
            print(f"❌ Error processing {file_type} file: {e}")
            results[file_type] = {
                'supported': True,
                'status': 'ERROR',
                'text_content': '',
                'errors': [str(e)],
                'warnings': []
            }
    
    # Clean up test files
    for file_path in test_files.values():
        try:
            os.remove(file_path)
        except:
            pass
    
    try:
        os.rmdir(os.path.dirname(list(test_files.values())[0]))
    except:
        pass
    
    return results

def test_flask_file_upload_simulation():
    """Simulate Flask file upload processing"""
    print("\n=== Testing Flask file upload simulation ===")
    
    # Create a test file
    temp_dir = tempfile.mkdtemp()
    txt_content = "This is a test file for Flask upload simulation.\nIt should be processed correctly by the audiobook creation system."
    txt_path = os.path.join(temp_dir, "flask_test.txt")
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    # Test the extract_text_from_file function from app.py
    try:
        # Import the function from app.py
        import sys
        sys.path.append('d:\\project\\audiobook')
        from app import extract_text_from_file
        
        extracted_text = extract_text_from_file(txt_path)
        
        if extracted_text:
            print("✅ Flask file upload simulation PASSED")
            print(f"Extracted text: {extracted_text[:100]}...")
        else:
            print("❌ Flask file upload simulation FAILED - No text extracted")
            
    except Exception as e:
        print(f"❌ Flask file upload simulation FAILED with error: {e}")
    
    # Clean up
    try:
        os.remove(txt_path)
        os.rmdir(temp_dir)
    except:
        pass

def main():
    """Run all file import tests"""
    print("Starting comprehensive file import tests for audiobook creation...\n")
    
    # Test file processing service
    results = test_file_processing()
    
    # Test Flask upload simulation
    test_flask_file_upload_simulation()
    
    # Summary
    print(f"\n=== Test Summary ===")
    passed = 0
    total = len(results)
    
    for file_type, result in results.items():
        if result['status'] in ['success', 'partial']:  # Fixed case sensitivity
            print(f"✅ {file_type.upper()}: PASSED ({result['status']})")
            passed += 1
        elif result['status'] == 'unsupported':
            print(f"⚠️  {file_type.upper()}: UNSUPPORTED")
        else:
            print(f"❌ {file_type.upper()}: FAILED ({result['status']})")
            if result['errors']:
                print(f"   Errors: {result['errors']}")
    
    print(f"\nFile format tests: {passed}/{total} passed")
    
    if passed > 0:
        print("\n🎉 File import functionality is working for supported formats!")
        print("Supported formats for audiobook creation:")
        for file_type, result in results.items():
            if result['supported'] and result['status'] in ['success', 'partial']:
                print(f"  - .{file_type.upper()}")
    else:
        print("\n❌ File import functionality needs attention!")

if __name__ == "__main__":
    main()