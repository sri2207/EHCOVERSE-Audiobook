"""
EchoVerse File Import Demo
Demonstrates how to import TXT, PDF, DOCX, and other files to create audiobooks
"""

import os
import tempfile
from services.file_service import FileProcessingService

def create_sample_files():
    """Create sample files for demonstration"""
    temp_dir = tempfile.mkdtemp()
    files = {}
    
    # Sample content
    content = """The Adventure of the Speckled Band

On glancing down at it, I observed that there was a slight fracture upon its surface;
and raising it to my lips, I detected a strong smell of bitter almonds.
The deduction was obvious. I sprang at the bell-rope, and pulled at it with all my strength.
The bell rang loudly, and a few moments later Dr. Watson entered the room.

"You have done some detective work of your own," said he, passing a sheet of paper to me.
"It is a report of the Coroner's inquiry into the death of Dr. Grimesby Roylott."
    
    "And what did they make of it?"
    
    "Nothing. The gypsies have been arrested and examined, but nothing incriminating
    was found in their possession. They stoutly deny any connection with the matter,
    and the police are at fault. It is a most mysterious affair."
    
    "But you have formed your own conclusions?"
    
    "Yes, I fancy I can see my way through it all now."
    
    "And what do you propose to do?"
    
    "To call upon Mr. Windibank this morning, and to make a few inquiries."
    
    "But what if he refuses to answer?"
    
    "Then I shall have recourse to other measures.""
    
    "What are they?"
    
    "I shall wire to France for a copy of the police report, and I shall also
    write to the landlord of the hotel at which Roylott stayed."
    
    "And what then?"
    
    "We shall see what we shall see."
    
    With this cryptic remark, Holmes leaned back in his chair and began to hum a tune."""

    # 1. Create TXT file
    txt_path = os.path.join(temp_dir, "sherlock_holmes.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    files['txt'] = txt_path
    
    # 2. Create HTML file
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>The Adventure of the Speckled Band</title>
</head>
<body>
    <h1>The Adventure of the Speckled Band</h1>
    <p>{content.replace(chr(10), '</p><p>')}</p>
</body>
</html>"""
    
    html_path = os.path.join(temp_dir, "sherlock_holmes.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    files['html'] = html_path
    
    print(f"📁 Created sample files in: {temp_dir}")
    return files

def demonstrate_file_processing():
    """Demonstrate file processing for audiobook creation"""
    print("🎧 EchoVerse - File Import Demonstration")
    print("=" * 50)
    
    # Create sample files
    sample_files = create_sample_files()
    
    # Initialize file processing service
    file_service = FileProcessingService()
    print("✅ File processing service ready")
    
    # Process each file
    for file_type, file_path in sample_files.items():
        print(f"\n--- Processing {file_type.upper()} file ---")
        
        # Get file info
        file_type_enum, mime_type = file_service.detect_file_type(file_path)
        print(f"📄 File type: {file_type_enum.value}")
        print(f"🏷️  MIME type: {mime_type}")
        
        # Process the file
        result = file_service.extract_text_from_file(file_path)
        
        # Display results
        print(f"📊 Status: {result.status.value}")
        print(f"📏 Text length: {len(result.text_content)} characters")
        print(f"⏱️  Processing time: {result.processing_time:.2f} seconds")
        
        if result.errors:
            print(f"❌ Errors: {result.errors}")
        if result.warnings:
            print(f"⚠️  Warnings: {result.warnings}")
        
        if result.text_content:
            # Show preview
            preview = result.text_content[:150].replace('\n', ' ')
            print(f"🔍 Text preview: {preview}...")
            
            # Show word count and estimated reading time
            word_count = len(result.text_content.split())
            reading_time = max(1, word_count // 200)  # ~200 WPM
            print(f"📈 Word count: {word_count}")
            print(f"⏱️  Estimated reading time: {reading_time} minutes")
            
            print("✅ File ready for audiobook creation!")
    
    # Clean up
    for file_path in sample_files.values():
        try:
            os.remove(file_path)
        except:
            pass
    try:
        os.rmdir(os.path.dirname(list(sample_files.values())[0]))
    except:
        pass
    
    print(f"\n🎉 Demonstration complete!")
    print("💡 Supported file formats for audiobook creation:")
    print("   • TXT - Plain text files")
    print("   • HTML - Web pages")
    print("   • PDF - Portable Document Format (if PyPDF2 installed)")
    print("   • DOCX - Microsoft Word documents (if python-docx installed)")
    print("\n📁 To create an audiobook:")
    print("   1. Upload your file through the web interface")
    print("   2. Select your preferred voice and settings")
    print("   3. The system will automatically extract text and generate audio")
    print("   4. Download your audiobook!")

if __name__ == "__main__":
    demonstrate_file_processing()