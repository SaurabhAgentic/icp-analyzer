from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Application configuration class."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        # Flask settings
        self.FLASK_ENV = os.getenv('FLASK_ENV', 'development')
        self.FLASK_DEBUG = self.FLASK_ENV == 'development'
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 5000))
        
        # Redis settings
        self.REDIS_URL = os.getenv('REDIS_URL')
        if self.REDIS_URL:
            # Parse Redis URL for individual components
            from urllib.parse import urlparse
            redis_url = urlparse(self.REDIS_URL)
            self.REDIS_HOST = redis_url.hostname
            self.REDIS_PORT = redis_url.port or 6379
            self.REDIS_PASSWORD = redis_url.password
            self.REDIS_DB = int(redis_url.path.lstrip('/') or 0)
        else:
            self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
            self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
            self.REDIS_DB = int(os.getenv('REDIS_DB', 0))
            self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
        
        # MongoDB settings
        self.MONGODB_URI = os.getenv('MONGODB_URI')
        if self.MONGODB_URI:
            # Parse MongoDB URI for individual components
            from urllib.parse import urlparse
            mongo_url = urlparse(self.MONGODB_URI)
            self.MONGODB_HOST = mongo_url.hostname
            self.MONGODB_PORT = mongo_url.port or 27017
            self.MONGODB_DB = mongo_url.path.lstrip('/') or 'icp_analyzer'
            self.MONGODB_USER = mongo_url.username
            self.MONGODB_PASSWORD = mongo_url.password
        else:
            self.MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
            self.MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
            self.MONGODB_DB = os.getenv('MONGODB_DB', 'icp_analyzer')
            self.MONGODB_USER = os.getenv('MONGODB_USER', '')
            self.MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')
        
        # Celery settings
        self.CELERY_BROKER_URL = self.REDIS_URL or self.get_redis_url()
        self.CELERY_RESULT_BACKEND = self.REDIS_URL or self.get_redis_url()
        self.CELERY_TASK_SERIALIZER = 'json'
        self.CELERY_RESULT_SERIALIZER = 'json'
        self.CELERY_ACCEPT_CONTENT = ['json']
        self.CELERY_TIMEZONE = 'UTC'
        self.CELERY_ENABLE_UTC = True
        
        # Rate limiting
        self.RATELIMIT_ENABLED = True
        self.RATELIMIT_STORAGE_URL = self.CELERY_BROKER_URL
        self.RATELIMIT_STRATEGY = 'fixed-window'
        self.RATELIMIT_DEFAULT = '100 per minute'
        
        # JWT settings
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', self.SECRET_KEY)
        self.JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
        
        # Monitoring settings
        self.METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))
        self.SENTRY_DSN = os.getenv('SENTRY_DSN', None)
        
        # File storage settings
        self.UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
        
        # Analysis settings
        self.MAX_URLS_PER_ANALYSIS = int(os.getenv('MAX_URLS_PER_ANALYSIS', 10))
        self.MAX_TESTIMONIALS_PER_URL = int(os.getenv('MAX_TESTIMONIALS_PER_URL', 100))
        self.ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', 300))  # 5 minutes
        
        # Cache settings
        self.CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')
        self.CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
        self.CACHE_KEY_PREFIX = os.getenv('CACHE_KEY_PREFIX', 'icp_analyzer')
        
        # Export settings
        self.EXPORT_FORMATS = ['pdf', 'pptx', 'docx', 'xlsx']
        self.MAX_EXPORT_SIZE = int(os.getenv('MAX_EXPORT_SIZE', 50 * 1024 * 1024))  # 50MB
        
        # Integration settings
        self.SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME', '')
        self.SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD', '')
        self.SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN', '')
        
        self.HUBSPOT_API_KEY = os.getenv('HUBSPOT_API_KEY', '')
        
        self.ZENDESK_EMAIL = os.getenv('ZENDESK_EMAIL', '')
        self.ZENDESK_API_TOKEN = os.getenv('ZENDESK_API_TOKEN', '')
        self.ZENDESK_SUBDOMAIN = os.getenv('ZENDESK_SUBDOMAIN', '')
    
    def get_redis_url(self) -> str:
        """Get Redis URL with authentication if configured."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_mongodb_url(self) -> str:
        """Get MongoDB URL with authentication if configured."""
        if self.MONGODB_URI:
            return self.MONGODB_URI
        
        auth = f"{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@" if self.MONGODB_USER and self.MONGODB_PASSWORD else ""
        return f"mongodb://{auth}{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
    
    def validate(self) -> bool:
        """Validate required configuration settings."""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'MONGODB_DB'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }

# Initialize global configuration instance
config = Config() 