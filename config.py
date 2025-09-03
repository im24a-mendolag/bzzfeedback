import os
from dotenv import load_dotenv

# Load .env variables if present
load_dotenv()

SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev')

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', '3306')),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'bzzfeedbackdb'),
}

