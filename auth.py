from db import get_connection
from crypto.hashing import hash_password, verify_password

def create_user(username, password, is_admin=0):
    conn = get_connection()
    c = conn.cursor()
    salt, hashed = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, ?)",
                  (username, hashed, salt, is_admin))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash, salt, is_admin FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        uid, stored_hash, salt, is_admin = row
        if verify_password(password, stored_hash, salt):
            return {"id": uid, "username": username, "is_admin": is_admin}
    return None

def ensure_admin():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE is_admin=1")
    exists = c.fetchone()
    conn.close()
    if not exists:
        create_user("admin", "admin123", is_admin=1)
