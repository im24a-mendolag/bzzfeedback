import os
import sys
import tempfile
import pytest

# Ensure project root is on sys.path so 'app' and 'scripts' are importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set test env BEFORE importing application modules so config picks it up
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("DB_NAME", "bzzfeedbackdb_test")
# Ensure the app's DB_CONFIG uses the test database
os.environ["MYSQL_DATABASE"] = os.environ["DB_NAME"]

from app.main import create_app
from scripts.init_db import main as init_db_main


@pytest.fixture(scope="session")
def app():
    # Initialize a clean test database
    init_db_main()
    app = create_app()
    app.config.update(
        TESTING=True,
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username: str, password: str):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def register(client, username: str, password: str, is_teacher: bool = False):
    data = {
        'username': username,
        'password': password,
        'password2': password,
    }
    if is_teacher:
        data['is_teacher'] = 'on'
    return client.post('/register', data=data, follow_redirects=True)


