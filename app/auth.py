from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db import query_one


class User(UserMixin):
    def __init__(self, user_id: int, email: str, display_name: str, role: str):
        self.id = str(user_id)
        self.email = email
        self.display_name = display_name
        self.role = role

    @staticmethod
    def get(user_id: str):
        row = query_one(
            "SELECT id, email, display_name, role FROM users WHERE id=%s",
            (user_id,),
        )
        if not row:
            return None
        return User(row["id"], row["email"], row["display_name"], row["role"])


def verify_login(email: str, password: str):
    row = query_one(
        "SELECT id, email, display_name, role, password_hash FROM users WHERE email=%s",
        (email,),
    )
    if not row:
        return None
    if not check_password_hash(row["password_hash"], password):
        return None
    return User(row["id"], row["email"], row["display_name"], row["role"])


def hash_password(password: str) -> str:
    return generate_password_hash(password)

