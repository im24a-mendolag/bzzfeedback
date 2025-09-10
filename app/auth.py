from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db import query_one


class User(UserMixin):
    def __init__(self, user_id: int, username: str, role: str):
        self.id = str(user_id)
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id: str):
        row = query_one(
            "SELECT id, username, role FROM users WHERE id=%s",
            (user_id,),
        )
        if not row:
            return None
        return User(row["id"], row["username"], row["role"])


def verify_login(username: str, password: str):
    row = query_one(
        "SELECT id, username, role, password_hash FROM users WHERE username=%s",
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
    return User(row["id"], row["username"], row["role"])


def hash_password(password: str) -> str:
    return generate_password_hash(password)

