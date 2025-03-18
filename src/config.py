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

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

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