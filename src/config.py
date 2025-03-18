import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Application Settings
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_APP = os.getenv('FLASK_APP', 'src/ui/app.py')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# Analysis Settings
MAX_DEPTH = os.getenv('MAX_DEPTH', 'comprehensive')
DEFAULT_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '30'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
VISUALIZATIONS_DIR = os.path.join(BASE_DIR, 'visualizations')

# Create directories if they don't exist
for directory in [DATA_DIR, REPORTS_DIR, VISUALIZATIONS_DIR]:
    os.makedirs(directory, exist_ok=True)

# File upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# Analysis settings
MAX_URLS_PER_ANALYSIS = 10
MAX_TESTIMONIALS_PER_URL = 100
ANALYSIS_TIMEOUT = 300  # 5 minutes

# Export settings
EXPORT_FORMATS = ['pdf', 'pptx', 'docx', 'xlsx']
MAX_EXPORT_SIZE = 50 * 1024 * 1024  # 50MB

# Analysis Configuration
ANALYSIS_CONFIG = {
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