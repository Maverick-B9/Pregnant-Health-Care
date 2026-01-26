# smart-healthcare-app/config.py
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') 
load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-please-change'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'smart_health_db'
    
    TF_MODEL_PATH = os.environ.get('TF_MODEL_PATH') or os.path.join('app', 'model_path.h5') # Path to your diagnostics.h5 model
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development' # Default to development
    DEBUG = FLASK_ENV == 'development'
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    # Ensure SECRET_KEY is strong and set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY') # Must be set in prod
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

key = os.environ.get('FLASK_CONFIG') or 'default'
current_config = config_by_name[key]