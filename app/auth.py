from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db import query_one


class User(UserMixin):
    def __init__(self, user_id: int, username: str, role: str, class_name: str = None):
        self.id = str(user_id)
        self.username = username
        self.role = role
        self.class_name = class_name

    @staticmethod
    def get(user_id: str):
        row = query_one(
            "SELECT id, username, role, class_name FROM users WHERE id=%s",
            (user_id,),
        )
        if not row:
            return None
        return User(row["id"], row["username"], row["role"], row["class_name"])


def verify_login(username: str, password: str):
    row = query_one(
        "SELECT id, username, role, class_name, password_hash FROM users WHERE username=%s",
        (username,),
    )
    if not row:
        return None
    try:
        if not check_password_hash(row["password_hash"], password):
            return None
    except Exception:
        # Stored hash is invalid/legacy. Treat as authentication failure without crashing.
        return None
    return User(row["id"], row["username"], row["role"], row["class_name"])


def hash_password(password: str) -> str:
    return generate_password_hash(password)

