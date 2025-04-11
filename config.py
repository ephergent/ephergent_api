import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_default_secret_key_for_dev')
    DEBUG = False
    TESTING = False
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    MAILGUN_LIST_ADDRESS = os.environ.get('MAILGUN_LIST_ADDRESS')
    MAILGUN_API_BASE_URL = "https://api.mailgun.net/v3"
    API_SECRET = os.environ.get('API_SECRET') # Load the API secret

    # Basic validation
    if not MAILGUN_API_KEY:
        raise ValueError("No MAILGUN_API_KEY set for Flask application")
    if not MAILGUN_LIST_ADDRESS:
        raise ValueError("No MAILGUN_LIST_ADDRESS set for Flask application")
    # Add validation for API_SECRET, especially in production
    # Consider adding:
    # if not API_SECRET and os.getenv('FLASK_CONFIG') == 'prod':
    #     raise ValueError("No API_SECRET set for Flask application in production")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use a different list for testing if needed
    # MAILGUN_LIST_ADDRESS = os.environ.get('TEST_MAILGUN_LIST_ADDRESS', Config.MAILGUN_LIST_ADDRESS)


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure SECRET_KEY is set in production
    if Config.SECRET_KEY == 'a_default_secret_key_for_dev':
         raise ValueError("SECRET_KEY must be set in production environment")


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
