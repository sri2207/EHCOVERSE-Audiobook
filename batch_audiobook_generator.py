#!/usr/bin/env python3
"""
Batch Audiobook Generator
Converts multiple text files to audiobooks with advanced options
"""

import os
import sys
import argparse
import glob
from pathlib import Path
from typing import List

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def batch_create_audiobooks(input_paths: List[str], output_dir: str = "", voice_type: str = "female_warm", 
                           rate: int = 175, volume: float = 0.9):
    """
    Create audiobooks from multiple text files
    
    Args:
        input_paths (List[str]): List of input file paths or glob patterns
        output_dir (str): Directory for output audio files
        voice_type (str): Voice type to use for narration
        rate (int): Speech rate (words per minute)
        volume (float): Speech volume (0.0 to 1.0)
    """
    try:
        # Import the text-to-speech function from the existing codebase
        from app import text_to_speech, extract_text_from_file, allowed_file
        
        # Expand glob patterns
        expanded_paths = []
        for path_pattern in input_paths:
            if '*' in path_pattern or '?' in path_pattern:
                # Handle glob patterns
                expanded_paths.extend(glob.glob(path_pattern))
            else:
                expanded_paths.append(path_pattern)
        
        # Validate and filter files
        valid_files = []
        for file_path in expanded_paths:
            if os.path.exists(file_path):
                # Check if file extension is allowed
                if allowed_file(file_path):
                    valid_files.append(file_path)
                else:
                    print(f"Warning: Skipping '{file_path}' - unsupported file type")
            else:
                print(f"Warning: Skipping '{file_path}' - file not found")
        
        if not valid_files:
            print("Error: No valid input files found.")
            return False
        
        # Create output directory if specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            output_dir = "."
        
        print(f"Processing {len(valid_files)} files...")
        print(f"Output directory: {output_dir}")
        print(f"Voice type: {voice_type}")
        print("-" * 50)
        
        # Process each file
        success_count = 0
        for i, input_file_path in enumerate(valid_files, 1):
            print(f"\n[{i}/{len(valid_files)}] Processing: {os.path.basename(input_file_path)}")
            
            try:
                # Extract text from file
                text = extract_text_from_file(input_file_path)
                
                if not text:
                    print(f"  ❌ Failed to extract text from {input_file_path}")
                    continue
                
                # Generate output filename
                input_path = Path(input_file_path)
                output_filename = input_path.stem + '.wav'
                output_file_path = os.path.join(output_dir, output_filename)
                
                # Convert text to speech
                success = text_to_speech(
                    text=text,
                    output_path=output_file_path,
                    voice_rate=rate,
                    voice_volume=volume,
                    voice_type=voice_type,
                    enable_naturalness=True,
                    continuous_flow=True,
                    enable_ai_features=False  # Disable AI features for faster processing
                )
                
                if success:
                    file_size = os.path.getsize(output_file_path) / (1024*1024)
                    print(f"  ✅ Success: {output_filename} ({file_size:.2f} MB)")
                    success_count += 1
                else:
                    print(f"  ❌ Failed to generate audiobook for {input_file_path}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {input_file_path}: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"Batch processing completed: {success_count}/{len(valid_files)} files successful")
        return success_count > 0
        
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        return False

def main():
    """Main function to parse arguments and create audiobooks"""
    parser = argparse.ArgumentParser(description="Batch create audiobooks from text files")
    parser.add_argument("input_files", nargs='+', help="Input text files or glob patterns (e.g., *.txt, docs/*.pdf)")
    parser.add_argument("-o", "--output-dir", help="Output directory for audio files (default: current directory)")
    parser.add_argument("-v", "--voice", choices=[
        "female_warm", "male_deep", "cheerful_energetic", "calm_meditative",
        "adventurous_explorer", "mysterious_storyteller", "romantic_dreamer",
        "wise_mentor", "playful_comedian", "confident_leader"
    ], default="female_warm", help="Voice type for narration")
    parser.add_argument("-r", "--rate", type=int, default=175, help="Speech rate in words per minute (80-280)")
    parser.add_argument("--volume", type=float, default=0.9, help="Speech volume (0.1-1.0)")
    
    args = parser.parse_args()
    
    print("🎙️  EchoVerse Batch Audiobook Generator")
    print("=" * 40)
    
    # Validate rate and volume
    args.rate = max(80, min(280, args.rate))
    args.volume = max(0.1, min(1.0, args.volume))
    
    # Create the audiobooks
    success = batch_create_audiobooks(
        input_paths=args.input_files,
        output_dir=args.output_dir if args.output_dir else "",
        voice_type=args.voice,
        rate=args.rate,
        volume=args.volume
    )
    
    if success:
        print("\n🎉 Batch audiobook generation completed!")
    else:
        print("\n💥 Batch audiobook generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()