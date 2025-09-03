import sys
import os
import mysql.connector
from werkzeug.security import generate_password_hash

# Ensure project root for config import
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import DB_CONFIG


def main():
    if len(sys.argv) != 3:
        print("Usage: python scripts/set_password.py <username> <new_password>")
        sys.exit(1)

    username = sys.argv[1]
    new_password = sys.argv[2]
    password_hash = generate_password_hash(new_password)

    cfg = DB_CONFIG.copy()
    # Respect configured database
    conn = mysql.connector.connect(**cfg)
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET password_hash=%s WHERE email=%s", (password_hash, username))
        conn.commit()
        if cur.rowcount == 0:
            print(f"No user found with username '{username}'.")
        else:
            print(f"Password updated for '{username}'.")
        cur.close()
    finally:
        conn.close()


if __name__ == '__main__':
    main()


