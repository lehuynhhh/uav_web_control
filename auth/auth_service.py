import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


def get_connection(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def register_user(db_path, username, password):
    username = username.strip()

    if not username or not password:
        return False, "Username and password are required"

    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing_user = cur.fetchone()

    if existing_user is not None:
        conn.close()
        return False, "Username already exists"

    password_hash = generate_password_hash(password)

    cur.execute(
        """
        INSERT INTO users (username, password_hash, role, status, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        """,
        (username, password_hash, "user", "pending")
    )

    conn.commit()
    conn.close()

    return True, "Register successful. Please wait for admin approval."


def login_user(db_path, username, password):
    username = username.strip()

    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, username, password_hash, role, status
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cur.fetchone()
    conn.close()

    if user is None:
        return False, "Invalid username or password", None

    if not check_password_hash(user["password_hash"], password):
        return False, "Invalid username or password", None

    if user["status"] == "pending":
        return False, "Your account is waiting for admin approval", None

    if user["status"] == "blocked":
        return False, "Your account has been blocked", None

    user_data = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "status": user["status"],
    }

    return True, "Login successful", user_data


def is_admin(user):
    return user is not None and user.get("role") == "admin"


def is_active_user(user):
    return user is not None and user.get("status") == "active"
