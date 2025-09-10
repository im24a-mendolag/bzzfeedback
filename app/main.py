from flask import Flask, request, g
import logging
from logging.handlers import RotatingFileHandler
import os
import time
from flask_login import LoginManager
from .routes import bp as routes_bp
from .auth import User
from .db import MySQLPool
from config import SECRET_KEY, LOG_DIR, LOG_LEVEL


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=SECRET_KEY)
    # init db pool
    MySQLPool.init_pool()

    # login manager
    login_manager = LoginManager()
    login_manager.login_view = "routes.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    app.register_blueprint(routes_bp)

    # Logging setup
    os.makedirs(LOG_DIR, exist_ok=True)
    app.logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    info_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'info.log'), maxBytes=1_000_000, backupCount=5, encoding='utf-8')
    info_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    info_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    info_handler.setFormatter(info_formatter)
    app.logger.addHandler(info_handler)

    error_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'error.log'), maxBytes=1_000_000, backupCount=5, encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
    error_handler.setFormatter(error_formatter)
    app.logger.addHandler(error_handler)

    # Example startup log
    app.logger.info('App initialized')

    # Per-request logging
    @app.before_request
    def _log_request_start():
        g._start_time = time.time()
        app.logger.info(f"REQ {request.method} {request.path} args={dict(request.args)}")

    @app.after_request
    def _log_request_end(response):
        try:
            duration_ms = int((time.time() - getattr(g, '_start_time', time.time())) * 1000)
        except Exception:
            duration_ms = -1
        app.logger.info(f"RES {request.method} {request.path} status={response.status_code} duration_ms={duration_ms}")
        return response

    @app.errorhandler(Exception)
    def _log_unhandled_error(e):
        app.logger.exception("Unhandled exception")
        # Re-raise in debug; otherwise show generic 500
        if app.debug:
            raise
        return ("Internal Server Error", 500)
    return app

