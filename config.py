"""
Configuration module for the AI-Enhanced Audiobook Generator
"""
import os
from pathlib import Path

# Base configuration
class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ai-audiobook-secret-key-2024'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'epub'}
    
    # Directory configuration
    BASE_DIR = Path(__file__).parent
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    AUDIO_FOLDER = BASE_DIR / 'audio_output'
    VOICE_SAMPLES_FOLDER = BASE_DIR / 'voice_samples'
    STATIC_FOLDER = BASE_DIR / 'static'
    TEMPLATES_FOLDER = BASE_DIR / 'templates'
    
    # Ensure directories exist
    for folder in [UPLOAD_FOLDER, AUDIO_FOLDER, VOICE_SAMPLES_FOLDER]:
        folder.mkdir(exist_ok=True)
    
    # API Configuration
    API_KEY = os.environ.get('AUDIOBOOK_API_KEY', 'demo-key-for-development')
    API_SERVICE_ENABLED = bool(API_KEY)
    
    # Translation settings
    AUTO_DETECT_ENABLED = True
    AUTO_TRANSLATE_ENABLED = True
    DEFAULT_TARGET_LANGUAGE = 'en'
    
    # TTS Settings
    DEFAULT_VOICE_RATE = 175
    DEFAULT_VOICE_VOLUME = 0.9
    DEFAULT_VOICE_TYPE = 'female_warm'
    
    # AI Features
    AI_FEATURES_ENABLED = True
    EMOTION_DETECTION_ENABLED = True
    NATURAL_SPEECH_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-change-this'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = 'development'):
    """Get configuration class by name"""
    return config.get(config_name, config['default'])