"""
Crypto Package - Paket Algoritma Kriptografi
=============================================

Package ini berisi implementasi berbagai algoritma kriptografi:

Modules:
- aes.py: AES-256 encryption (symmetric, military-grade)
- hashing.py: Password hashing dengan PBKDF2-HMAC-SHA256
- vigenere.py: Vigenère cipher (polyalphabetic substitution)

Author: Taufiq
Package: crypto
"""

__version__ = "1.0.0"
__author__ = "Taufiq"

# Import semua fungsi utama untuk kemudahan akses
from .aes import generate_key, encrypt_aes, decrypt_aes
from .hashing import hash_password, verify_password
from .vigenere import vigenere_encrypt, vigenere_decrypt

__all__ = [
    'generate_key',
    'encrypt_aes',
    'decrypt_aes',
    'hash_password',
    'verify_password',
    'vigenere_encrypt',
    'vigenere_decrypt',
]
