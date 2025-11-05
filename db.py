"""
Database Module - Modul Database SQLite
========================================

Module ini menangani semua operasi database:
- Koneksi ke SQLite database
- Inisialisasi tabel (users, messages)
- Schema database

Database: secure_messenger.db (SQLite)

Tabel:
1. users - Menyimpan data user dan kredensial
2. messages - Menyimpan pesan terenkripsi antar user

Author: Taufiq
Module: db.py
"""

import sqlite3

DB_NAME = "secure_messenger.db"

def get_connection():
    """
    Membuat koneksi ke database SQLite
    
    Returns:
        sqlite3.Connection: Object koneksi database
    
    Note:
        - Jika file database belum ada, akan dibuat otomatis
        - File database disimpan di direktori yang sama dengan script
    """
    return sqlite3.connect(DB_NAME)

def init_db():
    """
    Inisialisasi database dan buat tabel jika belum ada
    
    Fungsi ini akan membuat 2 tabel:
    
    1. Tabel users:
       - id: Primary key auto increment
       - username: Username unik (UNIQUE constraint)
       - password_hash: Hash password (PBKDF2-HMAC-SHA256)
       - salt: Salt unik untuk hashing
       - is_admin: Flag admin (0=user biasa, 1=admin)
    
    2. Tabel messages:
       - id: Primary key auto increment
       - sender: Username pengirim
       - receiver: Username penerima
       - content: Pesan terenkripsi (format: metadata::ciphertext)
       - timestamp: Waktu pengiriman (otomatis)
    
    Note:
        - Tabel dibuat dengan IF NOT EXISTS, aman dipanggil berkali-kali
        - Dipanggil saat aplikasi pertama kali dijalankan
    """
    conn = get_connection()
    c = conn.cursor()

    # Tabel users - Menyimpan kredensial dan info user
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    """)

    # Tabel messages - Menyimpan pesan terenkripsi
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
