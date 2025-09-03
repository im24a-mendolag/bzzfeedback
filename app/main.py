from flask import Flask
from flask_login import LoginManager
from .routes import bp as routes_bp
from .auth import User
from .db import MySQLPool
from config import SECRET_KEY


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
    return app

