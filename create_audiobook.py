#!/usr/bin/env python3
"""
Simple Audiobook Generator
Converts text files to audiobooks using EchoVerse TTS functionality
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def create_audiobook_from_file(input_file_path, output_file_path=None, voice_type="female_warm"):
    """
    Create an audiobook from a text file
    
    Args:
        input_file_path (str): Path to the input text file
        output_file_path (str): Path for the output audio file (optional)
        voice_type (str): Voice type to use for narration
    """
    try:
        # Import the text-to-speech function from the existing codebase
        from app import text_to_speech, extract_text_from_file
        
        # Validate input file
        if not os.path.exists(input_file_path):
            print(f"Error: Input file '{input_file_path}' not found.")
            return False
            
        # Extract text from file
        print(f"Extracting text from {input_file_path}...")
        text = extract_text_from_file(input_file_path)
        
        if not text:
            print("Error: Could not extract text from file.")
            return False
            
        # Generate output filename if not provided
        if not output_file_path:
            input_path = Path(input_file_path)
            output_file_path = input_path.with_suffix('.wav')
            
        # Convert text to speech
        print(f"Generating audiobook with {voice_type} voice...")
        print(f"Output will be saved to {output_file_path}")
        
        success = text_to_speech(
            text=text,
            output_path=str(output_file_path),
            voice_type=voice_type,
            enable_naturalness=True,
            continuous_flow=True
        )
        
        if success:
            print(f"✅ Audiobook successfully created: {output_file_path}")
            print(f"File size: {os.path.getsize(output_file_path) / (1024*1024):.2f} MB")
            return True
        else:
            print("❌ Failed to generate audiobook")
            return False
            
    except Exception as e:
        print(f"Error creating audiobook: {str(e)}")
        return False

def main():
    """Main function to parse arguments and create audiobook"""
    parser = argparse.ArgumentParser(description="Create audiobook from text file")
    parser.add_argument("input_file", help="Path to the input text file (.txt, .pdf, .docx)")
    parser.add_argument("-o", "--output", help="Output audio file path (default: same name as input with .wav extension)")
    parser.add_argument("-v", "--voice", choices=[
        "female_warm", "male_deep", "cheerful_energetic", "calm_meditative",
        "adventurous_explorer", "mysterious_storyteller", "romantic_dreamer",
        "wise_mentor", "playful_comedian", "confident_leader"
    ], default="female_warm", help="Voice type for narration")
    
    args = parser.parse_args()
    
    print("🎙️  EchoVerse Simple Audiobook Generator")
    print("=" * 40)
    
    # Create the audiobook
    success = create_audiobook_from_file(
        input_file_path=args.input_file,
        output_file_path=args.output,
        voice_type=args.voice
    )
    
    if success:
        print("\n🎉 Audiobook generation completed successfully!")
    else:
        print("\n💥 Audiobook generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()