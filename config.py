import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env variables if present
load_dotenv()

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev')

def get_db_config():
    """Get database configuration, handling Railway's MYSQL_URL and other formats"""
    # Debug: Print environment variables (remove in production)
    print(f"DEBUG: MYSQL_URL = {os.getenv('MYSQL_URL', 'NOT SET')}")
    print(f"DEBUG: DATABASE_URL = {os.getenv('DATABASE_URL', 'NOT SET')}")
    print(f"DEBUG: MYSQL_HOST = {os.getenv('MYSQL_HOST', 'NOT SET')}")
    
    # Check for Railway's MYSQL_URL first (Railway specific)
    mysql_url = os.getenv('MYSQL_URL')
    
    if mysql_url:
        print(f"DEBUG: Using MYSQL_URL: {mysql_url}")
        # Parse MYSQL_URL (format: mysql://user:password@host:port/database)
        parsed = urlparse(mysql_url)
        config = {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
        }
        print(f"DEBUG: Parsed config: {config}")
        return config
    
    # Check if Railway provides DATABASE_URL (common for cloud deployments)
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        print(f"DEBUG: Using DATABASE_URL: {database_url}")
        # Parse DATABASE_URL (format: mysql://user:password@host:port/database)
        parsed = urlparse(database_url)
        config = {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/'),
        }
        print(f"DEBUG: Parsed config: {config}")
        return config
    else:
        # Fallback to individual environment variables
        print("DEBUG: Using individual environment variables")
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'bzzfeedbackdb'),
        }
        print(f"DEBUG: Fallback config: {config}")
        return config

DB_CONFIG = get_db_config()

# Logging
LOG_DIR = os.getenv('LOG_DIR', os.path.join(os.path.dirname(__file__), 'logs'))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

