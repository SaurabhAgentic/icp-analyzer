import os
from dotenv import load_dotenv
from functools import lru_cache
from typing import Any, Union, Dict, List

# Load environment variables
load_dotenv()

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@lru_cache(maxsize=1)
def get_directories():
    """Lazy load directory paths."""
    return {
        'DATA_DIR': os.path.join(BASE_DIR, 'data'),
        'REPORTS_DIR': os.path.join(BASE_DIR, 'reports'),
        'VISUALIZATIONS_DIR': os.path.join(BASE_DIR, 'visualizations'),
        'UPLOAD_FOLDER': os.path.join(BASE_DIR, 'uploads')
    }

@lru_cache(maxsize=1)
def get_analysis_config():
    """Lazy load analysis configuration."""
    return {
        'basic': {
            'include_demographics': True,
            'include_psychographics': False,
            'include_behavior': False,
            'include_technical': False
        },
        'standard': {
            'include_demographics': True,
            'include_psychographics': True,
            'include_behavior': True,
            'include_technical': False
        },
        'comprehensive': {
            'include_demographics': True,
            'include_psychographics': True,
            'include_behavior': True,
            'include_technical': True
        }
    }

@lru_cache(maxsize=1)
def get_app_settings():
    """Lazy load application settings."""
    return {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'development'),
        'FLASK_APP': os.getenv('FLASK_APP', 'src/ui/app.py'),
        'DEBUG': os.getenv('DEBUG', 'True').lower() == 'true'
    }

@lru_cache(maxsize=1)
def get_analysis_settings():
    """Lazy load analysis settings."""
    return {
        'MAX_DEPTH': os.getenv('MAX_DEPTH', 'comprehensive'),
        'DEFAULT_TIMEOUT': int(os.getenv('DEFAULT_TIMEOUT', '30')),
        'MAX_RETRIES': int(os.getenv('MAX_RETRIES', '3')),
        'MAX_URLS_PER_ANALYSIS': 10,
        'MAX_TESTIMONIALS_PER_URL': 100,
        'ANALYSIS_TIMEOUT': 300  # 5 minutes
    }

@lru_cache(maxsize=1)
def get_export_settings():
    """Lazy load export settings."""
    return {
        'EXPORT_FORMATS': ['pdf', 'pptx', 'docx', 'xlsx'],
        'MAX_EXPORT_SIZE': 50 * 1024 * 1024  # 50MB
    }

@lru_cache(maxsize=1)
def get_openai_api_key():
    """Lazy load OpenAI API key."""
    return os.getenv('OPENAI_API_KEY')

# Convenience functions for accessing settings
def get_directory(name: str) -> str:
    """Get a directory path by name."""
    return get_directories()[name]

def get_analysis_setting(name: str) -> Any:
    """Get an analysis setting by name."""
    return get_analysis_settings()[name]

def get_app_setting(name: str) -> Any:
    """Get an application setting by name."""
    return get_app_settings()[name]

def get_export_setting(name: str) -> Any:
    """Get an export setting by name."""
    settings = get_export_settings()
    if name in settings:
        return settings[name]
    raise KeyError(f"Export setting '{name}' not found")

# Create directories if they don't exist
for directory in get_directories().values():
    os.makedirs(directory, exist_ok=True)

# Export commonly used settings for backward compatibility
REPORTS_DIR = get_directory('REPORTS_DIR')
DATA_DIR = get_directory('DATA_DIR')
VISUALIZATIONS_DIR = get_directory('VISUALIZATIONS_DIR')
UPLOAD_FOLDER = get_directory('UPLOAD_FOLDER')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Export analysis settings
DEFAULT_TIMEOUT = get_analysis_setting('DEFAULT_TIMEOUT')
MAX_RETRIES = get_analysis_setting('MAX_RETRIES')
MAX_URLS_PER_ANALYSIS = get_analysis_setting('MAX_URLS_PER_ANALYSIS')
MAX_TESTIMONIALS_PER_URL = get_analysis_setting('MAX_TESTIMONIALS_PER_URL')
ANALYSIS_TIMEOUT = get_analysis_setting('ANALYSIS_TIMEOUT')

# Export app settings
FLASK_ENV = get_app_setting('FLASK_ENV')
FLASK_APP = get_app_setting('FLASK_APP')
DEBUG = get_app_setting('DEBUG')

# Export export settings
EXPORT_FORMATS = get_export_setting('EXPORT_FORMATS')
MAX_EXPORT_SIZE = get_export_setting('MAX_EXPORT_SIZE') 