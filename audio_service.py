"""
Audio Service for audio file management and processing
"""
import os
import tempfile
import shutil
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class AudioFormat(Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"

class AudioQuality(Enum):
    """Audio quality levels"""
    LOW = "low"      # 22kHz, 64kbps
    MEDIUM = "medium"  # 44kHz, 128kbps
    HIGH = "high"    # 44kHz, 192kbps
    LOSSLESS = "lossless"  # 44kHz, uncompressed

@dataclass
class AudioMetadata:
    """Audio file metadata"""
    filename: str
    format: AudioFormat
    duration_seconds: float
    file_size_bytes: int
    sample_rate: int
    bitrate: Optional[int] = None
    channels: int = 1
    quality: AudioQuality = AudioQuality.MEDIUM

@dataclass
class AudioSegment:
    """Represents a segment of audio with metadata"""
    start_time: float
    end_time: float
    text: str
    character: Optional[str] = None
    emotion: Optional[str] = None
    file_path: Optional[str] = None

class AudioProcessingService:
    """Service for audio file management and basic processing"""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "audiobook_output")
        self.ensure_output_directory()
        
    def ensure_output_directory(self):
        """Ensure output directory exists"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"✅ Audio output directory ready: {self.output_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to create output directory: {e}")
            raise RuntimeError(f"Cannot create audio output directory: {e}")
    
    def generate_output_filename(self, base_name: str, format: AudioFormat = AudioFormat.WAV) -> str:
        """Generate unique output filename"""
        timestamp = int(time.time())
        clean_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')
        
        if not clean_name:
            clean_name = "audiobook"
        
        filename = f"{clean_name}_{timestamp}.{format.value}"
        return os.path.join(self.output_dir, filename)
    
    def validate_audio_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """Validate audio file"""
        errors = []
        
        if not os.path.exists(filepath):
            errors.append("Audio file does not exist")
            return False, errors
        
        if os.path.getsize(filepath) == 0:
            errors.append("Audio file is empty")
            return False, errors
        
        # Check file extension
        _, ext = os.path.splitext(filepath.lower())
        supported_extensions = [f".{fmt.value}" for fmt in AudioFormat]
        
        if ext not in supported_extensions:
            errors.append(f"Unsupported audio format: {ext}")
        
        return len(errors) == 0, errors
    
    def get_audio_info(self, filepath: str) -> Optional[AudioMetadata]:
        """Get audio file information"""
        try:
            if not os.path.exists(filepath):
                return None
            
            filename = os.path.basename(filepath)
            file_size = os.path.getsize(filepath)
            
            # Determine format from extension
            _, ext = os.path.splitext(filepath.lower())
            format_map = {
                '.wav': AudioFormat.WAV,
                '.mp3': AudioFormat.MP3,
                '.ogg': AudioFormat.OGG,
                '.flac': AudioFormat.FLAC
            }
            
            audio_format = format_map.get(ext, AudioFormat.WAV)
            
            # Basic metadata (would need audio library for detailed info)
            # For now, provide reasonable defaults
            metadata = AudioMetadata(
                filename=filename,
                format=audio_format,
                duration_seconds=0.0,  # Would need audio library to get actual duration
                file_size_bytes=file_size,
                sample_rate=44100,  # Default
                channels=1,
                quality=AudioQuality.MEDIUM
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to get audio info: {e}")
            return None
    
    def create_playlist(self, audio_files: List[str], playlist_name: str) -> str:
        """Create a simple playlist file"""
        try:
            playlist_path = os.path.join(self.output_dir, f"{playlist_name}.m3u")
            
            with open(playlist_path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                
                for audio_file in audio_files:
                    if os.path.exists(audio_file):
                        filename = os.path.basename(audio_file)
                        f.write(f"#EXTINF:-1,{filename}\n")
                        f.write(f"{audio_file}\n")
            
            logger.info(f"✅ Playlist created: {playlist_path}")
            return playlist_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create playlist: {e}")
            raise RuntimeError(f"Playlist creation failed: {e}")
    
    def copy_audio_file(self, source_path: str, destination_name: Optional[str] = None) -> str:
        """Copy audio file to output directory"""
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source audio file not found: {source_path}")
            
            if destination_name is None:
                destination_name = os.path.basename(source_path)
            
            destination_path = os.path.join(self.output_dir, destination_name)
            
            # Ensure we don't overwrite existing files
            counter = 1
            base_dest = destination_path
            while os.path.exists(destination_path):
                name, ext = os.path.splitext(base_dest)
                destination_path = f"{name}_{counter}{ext}"
                counter += 1
            
            shutil.copy2(source_path, destination_path)
            logger.info(f"✅ Audio file copied: {destination_path}")
            
            return destination_path
            
        except Exception as e:
            logger.error(f"❌ Failed to copy audio file: {e}")
            raise RuntimeError(f"Audio file copy failed: {e}")
    
    def organize_audio_files(self, audio_files: List[str], 
                           organization_type: str = "sequential") -> Dict[str, Any]:
        """Organize audio files according to specified scheme"""
        try:
            organized = {
                'files': [],
                'total_files': len(audio_files),
                'organization_type': organization_type,
                'created_at': time.time()
            }
            
            if organization_type == "sequential":
                # Simply number the files sequentially
                for i, audio_file in enumerate(audio_files, 1):
                    if os.path.exists(audio_file):
                        info = self.get_audio_info(audio_file)
                        organized['files'].append({
                            'sequence': i,
                            'original_path': audio_file,
                            'filename': os.path.basename(audio_file),
                            'metadata': info.__dict__ if info else None
                        })
            
            elif organization_type == "chapters":
                # Organize as chapters
                for i, audio_file in enumerate(audio_files, 1):
                    if os.path.exists(audio_file):
                        info = self.get_audio_info(audio_file)
                        organized['files'].append({
                            'chapter': i,
                            'title': f"Chapter {i}",
                            'original_path': audio_file,
                            'filename': os.path.basename(audio_file),
                            'metadata': info.__dict__ if info else None
                        })
            
            return organized
            
        except Exception as e:
            logger.error(f"❌ Failed to organize audio files: {e}")
            raise RuntimeError(f"Audio organization failed: {e}")
    
    def create_audio_manifest(self, organized_files: Dict[str, Any], 
                            manifest_name: str = "audiobook_manifest") -> str:
        """Create a manifest file for the audiobook"""
        try:
            import json
            
            manifest_path = os.path.join(self.output_dir, f"{manifest_name}.json")
            
            # Add additional metadata
            manifest = {
                **organized_files,
                'manifest_version': '1.0',
                'generated_by': 'AI-Enhanced Audiobook Generator',
                'total_duration_estimate': 0.0,
                'output_directory': self.output_dir
            }
            
            # Calculate total duration estimate if metadata is available
            total_duration = 0.0
            for file_info in manifest['files']:
                if file_info.get('metadata') and file_info['metadata'].get('duration_seconds'):
                    total_duration += file_info['metadata']['duration_seconds']
            
            manifest['total_duration_estimate'] = total_duration
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Audio manifest created: {manifest_path}")
            return manifest_path
            
        except Exception as e:
            logger.error(f"❌ Failed to create audio manifest: {e}")
            raise RuntimeError(f"Manifest creation failed: {e}")
    
    def cleanup_temporary_files(self, file_patterns: Optional[List[str]] = None):
        """Clean up temporary audio files"""
        try:
            if file_patterns is None:
                file_patterns = ["temp_*.wav", "segment_*.wav", "*.tmp"]
            
            cleaned_count = 0
            
            for pattern in file_patterns:
                import glob
                matching_files = glob.glob(os.path.join(self.output_dir, pattern))
                
                for file_path in matching_files:
                    try:
                        os.remove(file_path)
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"⚠️ Could not remove {file_path}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"✅ Cleaned up {cleaned_count} temporary files")
            
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")
    
    def get_output_directory_info(self) -> Dict[str, Any]:
        """Get information about the output directory"""
        try:
            if not os.path.exists(self.output_dir):
                return {'exists': False}
            
            files = os.listdir(self.output_dir)
            audio_files = [f for f in files if any(f.lower().endswith(f'.{fmt.value}') for fmt in AudioFormat)]
            
            total_size = 0
            file_info = []
            
            for filename in audio_files:
                filepath = os.path.join(self.output_dir, filename)
                file_size = os.path.getsize(filepath)
                total_size += file_size
                
                file_info.append({
                    'filename': filename,
                    'size_bytes': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2),
                    'modified_time': os.path.getmtime(filepath)
                })
            
            return {
                'exists': True,
                'path': self.output_dir,
                'total_files': len(audio_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'files': file_info
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get directory info: {e}")
            return {'error': str(e)}
    
    def create_batch_processing_plan(self, text_segments: List[Dict[str, Any]], 
                                   base_filename: str) -> List[Dict[str, Any]]:
        """Create a plan for batch processing multiple text segments"""
        try:
            processing_plan = []
            
            for i, segment in enumerate(text_segments):
                segment_plan = {
                    'segment_id': i + 1,
                    'text': segment.get('text', ''),
                    'character': segment.get('character', 'narrator'),
                    'emotion': segment.get('emotion', 'neutral'),
                    'intensity': segment.get('intensity', 0.5),
                    'output_filename': self.generate_output_filename(f"{base_filename}_segment_{i+1}"),
                    'estimated_duration': len(segment.get('text', '').split()) / 200 * 60,  # ~200 WPM
                    'priority': segment.get('priority', 'normal')
                }
                
                processing_plan.append(segment_plan)
            
            logger.info(f"✅ Created processing plan for {len(processing_plan)} segments")
            return processing_plan
            
        except Exception as e:
            logger.error(f"❌ Failed to create processing plan: {e}")
            raise RuntimeError(f"Processing plan creation failed: {e}")
    
    def validate_processing_plan(self, processing_plan: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate a processing plan"""
        errors = []
        
        try:
            if not processing_plan:
                errors.append("Processing plan is empty")
                return False, errors
            
            total_estimated_duration = 0
            
            for i, segment in enumerate(processing_plan):
                segment_id = segment.get('segment_id', i + 1)
                
                # Check required fields
                if not segment.get('text'):
                    errors.append(f"Segment {segment_id}: No text content")
                
                if not segment.get('output_filename'):
                    errors.append(f"Segment {segment_id}: No output filename specified")
                
                # Check output directory is writable
                output_file = segment.get('output_filename')
                if output_file:
                    output_dir = os.path.dirname(output_file)
                    if not os.access(output_dir, os.W_OK):
                        errors.append(f"Segment {segment_id}: Output directory not writable: {output_dir}")
                
                # Accumulate duration
                duration = segment.get('estimated_duration', 0)
                if isinstance(duration, (int, float)):
                    total_estimated_duration += duration
            
            # Check if total duration is reasonable
            if total_estimated_duration > 24 * 60 * 60:  # 24 hours
                errors.append(f"Total estimated duration too long: {total_estimated_duration/3600:.1f} hours")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Plan validation error: {e}")
            return False, errors
    
    def get_audio_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed audio files"""
        try:
            dir_info = self.get_output_directory_info()
            
            if not dir_info.get('exists'):
                return {'no_data': True}
            
            stats = {
                'total_files': dir_info.get('total_files', 0),
                'total_size_mb': dir_info.get('total_size_mb', 0),
                'average_file_size_mb': 0,
                'file_formats': {},
                'creation_times': []
            }
            
            files = dir_info.get('files', [])
            
            if files:
                stats['average_file_size_mb'] = round(
                    sum(f['size_mb'] for f in files) / len(files), 2
                )
                
                # Count file formats
                for file_info in files:
                    filename = file_info['filename']
                    _, ext = os.path.splitext(filename.lower())
                    ext = ext.lstrip('.')
                    
                    if ext in stats['file_formats']:
                        stats['file_formats'][ext] += 1
                    else:
                        stats['file_formats'][ext] = 1
                
                # Get creation times
                stats['creation_times'] = [f['modified_time'] for f in files]
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get audio statistics: {e}")
            return {'error': str(e)}