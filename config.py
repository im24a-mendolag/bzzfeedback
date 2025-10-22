import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env variables if present
load_dotenv()

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev')

def get_db_config():
    """Get database configuration, handling Railway's MYSQL_URL and other formats"""
    # Check for Railway's MYSQL_URL first (Railway specific)
    mysql_url = os.getenv('MYSQL_URL')
    
    if mysql_url:
        # Parse MYSQL_URL (format: mysql://user:password@host:port/database)
        parsed = urlparse(mysql_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
        }
    
    # Check if Railway provides DATABASE_URL (common for cloud deployments)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL (format: mysql://user:password@host:port/database)
        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
        }
    else:
        # Fallback to individual environment variables
        return {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'bzzfeedbackdb'),
        }

DB_CONFIG = get_db_config()

# Logging
LOG_DIR = os.getenv('LOG_DIR', os.path.join(os.path.dirname(__file__), 'logs'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

