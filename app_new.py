"""
AI-Enhanced Audiobook Generator - Modular Flask Application
Professional, clean, and maintainable architecture
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from flask import Flask, render_template, request, send_file, jsonify, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Import our service modules
try:
    from config import Config, get_config
    from services.language_service import LanguageService, LanguageDetectionResult, TranslationResult
    from services.text_service import TextProcessingService, EmotionType, TextAnalysis
    from services.voice_service import VoiceService, VoiceSettings, VoiceGender, VoicePersonality
    from services.file_service import FileProcessingService, ProcessingResult, FileType
    from services.audio_service import AudioProcessingService, AudioFormat
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Please ensure all service modules are available")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudiobookApp:
    """Main application class with clean service integration"""
    
    def __init__(self, config_name: str = 'development'):
        self.config = get_config(config_name)
        self.app = self._create_app()
        self._initialize_services()
        self._register_routes()
        self._setup_error_handlers()
    
    def _create_app(self) -> Flask:
        """Create and configure Flask application"""
        app = Flask(__name__)
        app.config.from_object(self.config)
        
        # Ensure required directories exist
        self._ensure_directories()
        
        return app
    
    def _ensure_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.config.UPLOAD_FOLDER,
            self.config.AUDIO_FOLDER,
            self.config.VOICE_SAMPLES_FOLDER
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Directory ready: {directory}")
    
    def _initialize_services(self):
        """Initialize all application services"""
        try:
            self.language_service = LanguageService()
            self.text_service = TextProcessingService()
            self.voice_service = VoiceService()
            self.file_service = FileProcessingService()
            self.audio_service = AudioProcessingService(self.config.AUDIO_FOLDER)
            
            logger.info("✅ All services initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize services: {e}")
    
    def _register_routes(self):
        """Register all application routes"""
        
        @self.app.route('/')
        def index():
            """Main application page"""
            try:
                # Get service status information
                service_status = {
                    'language_service': self._check_service_health(self.language_service),
                    'voice_service': self._check_service_health(self.voice_service),
                    'file_service': self._check_service_health(self.file_service),
                    'audio_service': self._check_service_health(self.audio_service)
                }
                
                # Get available voices and languages
                available_voices = self.voice_service.get_available_voices()
                supported_languages = self.language_service.get_supported_languages()
                
                return render_template('index_new.html',
                    service_status=service_status,
                    available_voices=available_voices[:10],  # Limit for UI
                    supported_languages=supported_languages,
                    config={
                        'max_file_size_mb': self.config.MAX_CONTENT_LENGTH // (1024 * 1024),
                        'supported_formats': self.file_service.get_supported_extensions()
                    }
                )
                
            except Exception as e:
                logger.error(f"❌ Index page error: {e}")
                return render_template('error.html', error="Application initialization error"), 500
        
        @self.app.route('/api/detect-language', methods=['POST'])
        def detect_language():
            """Detect language of uploaded text or file"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                text_content = data.get('text', '')
                file_path = data.get('file_path', '')
                
                # Extract text from file if file path provided
                if file_path and not text_content:
                    result = self.file_service.extract_text_from_file(file_path)
                    if result.status.value == 'success':
                        text_content = result.text_content
                    else:
                        return jsonify({'error': 'Failed to extract text from file'}), 400
                
                if not text_content.strip():
                    return jsonify({'error': 'No text content to analyze'}), 400
                
                # Detect language
                detection_result = self.language_service.detect_language(text_content)
                
                return jsonify({
                    'detected_language': detection_result.language_code,
                    'language_name': detection_result.language_name,
                    'confidence': detection_result.confidence,
                    'is_reliable': detection_result.is_reliable,
                    'text_sample': text_content[:200] + ('...' if len(text_content) > 200 else '')
                })
                
            except Exception as e:
                logger.error(f"❌ Language detection error: {e}")
                return jsonify({'error': f'Language detection failed: {str(e)}'}), 500
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload_file():
            """Handle file upload and processing"""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file uploaded'}), 400
                
                file = request.files['file']
                if not file.filename or file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                if not self._allowed_file(file.filename):
                    return jsonify({'error': 'File type not supported'}), 400
                
                # Secure filename and save
                filename = secure_filename(file.filename)
                file_path = os.path.join(self.config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                
                # Process the file
                processing_result = self.file_service.extract_text_from_file(file_path)
                
                response_data = {
                    'filename': filename,
                    'file_path': file_path,
                    'status': processing_result.status.value,
                    'text_content': processing_result.text_content,
                    'metadata': {
                        'word_count': processing_result.metadata.word_count,
                        'file_size_mb': round(processing_result.metadata.size_bytes / (1024 * 1024), 2),
                        'estimated_reading_time': processing_result.metadata.estimated_reading_time
                    },
                    'errors': processing_result.errors,
                    'warnings': processing_result.warnings
                }
                
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"❌ File upload error: {e}")
                return jsonify({'error': f'File upload failed: {str(e)}'}), 500
        
        @self.app.route('/api/analyze-text', methods=['POST'])
        def analyze_text():
            """Analyze text for emotion, themes, and other characteristics"""
            try:
                data = request.get_json()
                text_content = data.get('text', '')
                
                if not text_content.strip():
                    return jsonify({'error': 'No text content provided'}), 400
                
                # Perform comprehensive text analysis
                analysis = self.text_service.analyze_text_comprehensive(text_content)
                
                return jsonify({
                    'word_count': analysis.word_count,
                    'sentence_count': analysis.sentence_count,
                    'paragraph_count': analysis.paragraph_count,
                    'reading_level': analysis.reading_level,
                    'genre_hints': analysis.genre_hints,
                    'themes': analysis.themes,
                    'characters': analysis.characters,
                    'emotion_analysis': {
                        'dominant_emotion': analysis.emotion_analysis.dominant_emotion.value,
                        'intensity': analysis.emotion_analysis.intensity,
                        'confidence': analysis.emotion_analysis.confidence,
                        'emotion_scores': analysis.emotion_analysis.emotion_scores
                    }
                })
                
            except Exception as e:
                logger.error(f"❌ Text analysis error: {e}")
                return jsonify({'error': f'Text analysis failed: {str(e)}'}), 500
        
        @self.app.route('/api/translate', methods=['POST'])
        def translate_text():
            """Translate text to target language"""
            try:
                data = request.get_json()
                text_content = data.get('text', '')
                target_language = data.get('target_language', 'en')
                source_language = data.get('source_language', 'auto')
                
                if not text_content.strip():
                    return jsonify({'error': 'No text content provided'}), 400
                
                # Perform translation
                translation_result = self.language_service.translate_text(
                    text_content, target_language, source_language
                )
                
                return jsonify({
                    'translated_text': translation_result.translated_text,
                    'source_language': translation_result.source_language,
                    'target_language': translation_result.target_language,
                    'confidence': translation_result.confidence
                })
                
            except Exception as e:
                logger.error(f"❌ Translation error: {e}")
                return jsonify({'error': f'Translation failed: {str(e)}'}), 500
        
        @self.app.route('/api/generate-audio', methods=['POST'])
        def generate_audio():
            """Generate audiobook from text"""
            try:
                data = request.get_json()
                text_content = data.get('text', '')
                settings = data.get('settings', {})
                
                if not text_content.strip():
                    return jsonify({'error': 'No text content provided'}), 400
                
                # Analyze text for emotion
                analysis = self.text_service.analyze_text_comprehensive(text_content)
                emotion_type = analysis.emotion_analysis.dominant_emotion
                intensity = analysis.emotion_analysis.intensity
                
                # Configure voice settings
                voice_settings = VoiceSettings(
                    rate=settings.get('rate', 180),
                    volume=settings.get('volume', 0.9),
                    voice_id=settings.get('voice_id'),
                    gender=VoiceGender(settings.get('gender', 'neutral')),
                    personality=VoicePersonality(settings.get('personality', 'narrator'))
                )
                
                # Apply emotion adjustments
                emotion_settings = self.voice_service.adjust_for_emotion(emotion_type, intensity)
                
                # Enhance text for natural speech
                enhanced_text = self.text_service.enhance_text_for_speech(
                    text_content, emotion_type, intensity, 
                    continuous_flow=settings.get('continuous_flow', True)
                )
                
                # Generate audio filename
                audio_filename = self.audio_service.generate_output_filename(
                    settings.get('filename', 'audiobook'),
                    AudioFormat.WAV
                )
                
                # Generate speech
                success = self.voice_service.synthesize_speech(
                    enhanced_text, audio_filename, emotion_type, intensity
                )
                
                if success:
                    # Get audio metadata
                    audio_info = self.audio_service.get_audio_info(audio_filename)
                    
                    return jsonify({
                        'success': True,
                        'audio_file': os.path.basename(audio_filename),
                        'audio_path': audio_filename,
                        'metadata': audio_info.__dict__ if audio_info else None,
                        'text_analysis': {
                            'emotion': emotion_type.value,
                            'intensity': intensity,
                            'word_count': analysis.word_count,
                            'estimated_duration': analysis.word_count / 180 * 60  # ~180 WPM
                        }
                    })
                else:
                    return jsonify({'error': 'Audio generation failed'}), 500
                
            except Exception as e:
                logger.error(f"❌ Audio generation error: {e}")
                return jsonify({'error': f'Audio generation failed: {str(e)}'}), 500
        
        @self.app.route('/api/download/<filename>')
        def download_file(filename):
            """Download generated audio file"""
            try:
                file_path = os.path.join(self.config.AUDIO_FOLDER, secure_filename(filename))
                
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404
                
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='audio/wav'
                )
                
            except Exception as e:
                logger.error(f"❌ Download error: {e}")
                return jsonify({'error': 'Download failed'}), 500
        
        @self.app.route('/api/voices')
        def get_voices():
            """Get available TTS voices"""
            try:
                language_code = request.args.get('language', None)
                voices = self.voice_service.get_available_voices(language_code)
                
                voice_data = []
                for voice in voices:
                    voice_data.append({
                        'id': voice.id,
                        'name': voice.name,
                        'gender': voice.gender.value,
                        'language': voice.language,
                        'language_code': voice.language_code,
                        'quality': voice.quality,
                        'is_default': voice.is_default
                    })
                
                return jsonify({'voices': voice_data})
                
            except Exception as e:
                logger.error(f"❌ Get voices error: {e}")
                return jsonify({'error': 'Failed to get voices'}), 500
        
        @self.app.route('/api/voice-preview', methods=['POST'])
        def preview_voice():
            """Preview a selected voice"""
            try:
                data = request.get_json()
                voice_id = data.get('voice_id')
                preview_text = data.get('text', 'This is a preview of the selected voice.')
                
                success = self.voice_service.preview_voice(preview_text, voice_id)
                
                return jsonify({'success': success})
                
            except Exception as e:
                logger.error(f"❌ Voice preview error: {e}")
                return jsonify({'error': 'Voice preview failed'}), 500
        
        @self.app.route('/api/status')
        def get_status():
            """Get application and service status"""
            try:
                status = {
                    'application': 'running',
                    'services': {
                        'language_service': self._check_service_health(self.language_service),
                        'text_service': self._check_service_health(self.text_service),
                        'voice_service': self._check_service_health(self.voice_service),
                        'file_service': self._check_service_health(self.file_service),
                        'audio_service': self._check_service_health(self.audio_service)
                    },
                    'statistics': {
                        'audio_files': self.audio_service.get_audio_statistics(),
                        'supported_languages': len(self.language_service.get_supported_languages()),
                        'available_voices': len(self.voice_service.get_available_voices())
                    }
                }
                
                return jsonify(status)
                
            except Exception as e:
                logger.error(f"❌ Status check error: {e}")
                return jsonify({'error': 'Status check failed'}), 500
    
    def _setup_error_handlers(self):
        """Setup global error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return render_template('error.html', 
                error="Page not found", 
                message="The requested page could not be found."), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return render_template('error.html',
                error="Internal server error",
                message="An unexpected error occurred. Please try again."), 500
        
        @self.app.errorhandler(413)
        def file_too_large(error):
            return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    
    def _allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'docx', 'html'})
    
    def _check_service_health(self, service) -> Dict[str, Any]:
        """Check health status of a service"""
        try:
            if hasattr(service, 'get_voice_info'):
                # Voice service
                info = service.get_voice_info()
                return {'status': 'healthy', 'details': info}
            elif hasattr(service, 'get_supported_languages'):
                # Language service
                languages = service.get_supported_languages()
                return {'status': 'healthy', 'supported_languages': len(languages)}
            elif hasattr(service, 'get_supported_extensions'):
                # File service
                extensions = service.get_supported_extensions()
                return {'status': 'healthy', 'supported_extensions': extensions}
            elif hasattr(service, 'get_audio_statistics'):
                # Audio service
                stats = service.get_audio_statistics()
                return {'status': 'healthy', 'statistics': stats}
            else:
                return {'status': 'healthy', 'details': 'Service available'}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def run(self, debug: bool = False, port: int = 5000):
        """Run the Flask application"""
        logger.info(f"🚀 Starting AI-Enhanced Audiobook Generator on port {port}")
        self.app.run(debug=debug, port=port, host='0.0.0.0')

# Application factory
def create_app(config_name: str = 'development') -> Flask:
    """Create Flask application instance"""
    audiobook_app = AudiobookApp(config_name)
    return audiobook_app.app

# For direct execution
if __name__ == '__main__':
    import sys
    
    # Check command line arguments
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'development'
    debug_mode = '--debug' in sys.argv
    
    try:
        audiobook_app = AudiobookApp(config_name)
        audiobook_app.run(debug=debug_mode)
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        sys.exit(1)