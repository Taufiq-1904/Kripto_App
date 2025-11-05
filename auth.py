"""
Authentication Module - Modul Autentikasi Pengguna
==================================================

Module ini menangani semua operasi autentikasi pengguna:
- Registrasi user baru
- Login/verifikasi kredensial
- Password hashing untuk keamanan
- Manajemen admin

Author: Taufiq
Module: auth.py
"""

from db import get_connection
from crypto.hashing import hash_password, verify_password

def create_user(username, password, is_admin=0):
    """
    Membuat user baru dalam database
    
    Fungsi ini akan:
    1. Hash password menggunakan PBKDF2 dengan salt
    2. Simpan user ke database dengan password yang sudah di-hash
    
    Args:
        username (str): Username unik untuk user baru
        password (str): Password plaintext (akan di-hash)
        is_admin (int): 0 untuk user biasa, 1 untuk admin (default: 0)
    
    Returns:
        bool: True jika berhasil, False jika username sudah ada atau error
    
    Security:
        - Password TIDAK disimpan dalam bentuk plaintext
        - Menggunakan salt unik untuk setiap user
        - Hash menggunakan PBKDF2-HMAC-SHA256 dengan 100.000 iterasi
    """
    conn = get_connection()
    c = conn.cursor()
    salt, hashed = hash_password(password)  # Hash password dengan salt
    try:
        c.execute("INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, ?)",
                  (username, hashed, salt, is_admin))
        conn.commit()
        return True
    except Exception:
        # Gagal insert (biasanya karena username sudah ada - UNIQUE constraint)
        return False
    finally:
        conn.close()

def login(username, password):
    """
    Verifikasi kredensial login user
    
    Fungsi ini memverifikasi username dan password dengan:
    1. Ambil data user dari database (hash dan salt)
    2. Hash password input dengan salt yang sama
    3. Bandingkan hasil hash dengan hash tersimpan
    
    Args:
        username (str): Username yang login
        password (str): Password plaintext dari user
    
    Returns:
        dict: Dictionary berisi data user jika login berhasil
              {"id": user_id, "username": username, "is_admin": 0/1}
        None: Jika login gagal (username tidak ada atau password salah)
    
    Security:
        - Password tidak pernah disimpan atau dibandingkan dalam plaintext
        - Menggunakan constant-time comparison untuk mencegah timing attacks
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, password_hash, salt, is_admin FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row:
        uid, stored_hash, salt, is_admin = row
        # Verifikasi password dengan membandingkan hash
        if verify_password(password, stored_hash, salt):
            return {"id": uid, "username": username, "is_admin": is_admin}
    return None

def ensure_admin():
    """
    Memastikan ada akun admin default dalam sistem
    
    Fungsi ini mengecek apakah ada user dengan hak admin.
    Jika tidak ada, akan membuat akun admin default.
    
    Default admin:
        - Username: admin
        - Password: admin123
        - is_admin: 1
    
    Note:
        Fungsi ini biasanya dipanggil saat aplikasi pertama kali dijalankan
        untuk memastikan selalu ada akun admin yang bisa digunakan.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE is_admin=1")
    exists = c.fetchone()
    conn.close()
    
    if not exists:
        # Tidak ada admin, buat akun admin default
        create_user("admin", "admin123", is_admin=1)
