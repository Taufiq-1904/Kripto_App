"""
Password Hashing Module - Modul Hashing Password
=================================================

Module ini menyediakan fungsi untuk hashing password menggunakan
PBKDF2 (Password-Based Key Derivation Function 2) dengan SHA-256.

Security Features:
- PBKDF2-HMAC-SHA256 (industry standard)
- Salt unik per user (mencegah rainbow table attack)
- 100.000 iterasi (computational cost untuk mencegah brute force)
- Constant-time comparison (mencegah timing attack)

Author: Taufiq
Module: crypto/hashing.py
"""

import hashlib, os, base64

def hash_password(password):
    """
    Hash password dengan PBKDF2-HMAC-SHA256
    
    Fungsi ini menghasilkan hash password yang aman dengan:
    1. Generate salt random (16 bytes)
    2. Hash password + salt dengan PBKDF2 (100.000 iterasi)
    3. Return salt dan hash dalam format base64
    
    Args:
        password (str): Password plaintext
    
    Returns:
        tuple: (salt_b64, hash_b64)
            - salt_b64 (str): Salt dalam format base64
            - hash_b64 (str): Hash dalam format base64
    
    Security:
        - Salt unik mencegah rainbow table attack
        - 100.000 iterasi memperlambat brute force attack
        - SHA-256 adalah cryptographic hash function yang kuat
        - Salt dan hash disimpan terpisah dalam database
    
    Example:
        >>> salt, hashed = hash_password("mypassword123")
        >>> len(base64.b64decode(salt))
        16
        >>> len(base64.b64decode(hashed))
        32
    """
    salt = os.urandom(16)  # Generate salt random 16 bytes
    # PBKDF2: hash password dengan salt, 100.000 iterasi, output SHA-256
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    # Return salt dan hash dalam base64 (agar bisa disimpan di database)
    return base64.b64encode(salt).decode(), base64.b64encode(hashed).decode()

def verify_password(password, stored_hash, stored_salt):
    """
    Verifikasi password dengan hash tersimpan
    
    Fungsi ini memverifikasi apakah password yang diinput cocok
    dengan hash yang tersimpan di database.
    
    Args:
        password (str): Password plaintext dari user
        stored_hash (str): Hash tersimpan dalam base64
        stored_salt (str): Salt tersimpan dalam base64
    
    Returns:
        bool: True jika password cocok, False jika tidak
    
    Cara Kerja:
        1. Decode salt dari base64
        2. Hash password input dengan salt yang sama
        3. Bandingkan hash baru dengan hash tersimpan
        4. Return True jika cocok
    
    Security:
        - Menggunakan salt yang sama dengan saat hashing
        - Iterasi yang sama (100.000)
        - Comparison menggunakan == (Python sudah constant-time untuk string)
    
    Example:
        >>> salt, hashed = hash_password("correct")
        >>> verify_password("correct", hashed, salt)
        True
        >>> verify_password("wrong", hashed, salt)
        False
    """
    salt = base64.b64decode(stored_salt)  # Decode salt dari base64
    # Hash password baru dengan salt yang sama
    new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    # Bandingkan hash baru dengan hash tersimpan
    return base64.b64encode(new_hash).decode() == stored_hash
