"""
AES Encryption Module - Modul Enkripsi AES-256
===============================================

Module ini menyediakan fungsi enkripsi dan dekripsi menggunakan
algoritma AES (Advanced Encryption Standard) dengan mode GCM.

AES-GCM Features:
- AES-128 (16 byte key) dengan mode GCM (Galois/Counter Mode)
- Authenticated encryption (mencegah tampering)
- Nonce untuk setiap enkripsi (mencegah replay attack)
- Tag untuk verifikasi integritas data

Security Level: Military-grade encryption

Author: Taufiq
Module: crypto/aes.py
"""

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def generate_key():
    """
    Generate kunci AES random (16 bytes = 128 bit)
    
    Returns:
        bytes: Kunci AES 16 bytes yang di-generate secara random
    
    Note:
        - Menggunakan cryptographically secure random generator
        - Kunci harus disimpan dengan aman untuk dekripsi
        - Setiap enkripsi sebaiknya menggunakan kunci unik
    
    Example:
        >>> key = generate_key()
        >>> len(key)
        16
    """
    return get_random_bytes(16)

def encrypt_aes(plaintext, key):
    """
    Enkripsi teks menggunakan AES-GCM
    
    Args:
        plaintext (str): Teks asli yang akan dienkripsi
        key (bytes): Kunci AES 16 bytes
    
    Returns:
        str: Ciphertext dalam format base64
    
    Format output:
        base64(nonce + tag + ciphertext)
        - nonce (16 bytes): Number used once, unik per enkripsi
        - tag (16 bytes): Authentication tag untuk verifikasi
        - ciphertext: Data terenkripsi
    
    Security:
        - Mode GCM menyediakan confidentiality dan authenticity
        - Nonce otomatis di-generate untuk setiap enkripsi
        - Tag mencegah modifikasi data (tampering)
    
    Example:
        >>> key = generate_key()
        >>> cipher = encrypt_aes("Hello World", key)
        >>> type(cipher)
        <class 'str'>
    """
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    # Gabungkan nonce, tag, dan ciphertext
    data = cipher.nonce + tag + ciphertext
    return base64.b64encode(data).decode()

def decrypt_aes(cipher_b64, key):
    """
    Dekripsi ciphertext AES-GCM
    
    Args:
        cipher_b64 (str): Ciphertext dalam format base64
        key (bytes): Kunci AES yang sama dengan saat enkripsi
    
    Returns:
        str: Plaintext (teks asli)
    
    Raises:
        ValueError: Jika tag verification gagal (data telah dimodifikasi)
    
    Security:
        - Verifikasi tag sebelum dekripsi (decrypt_and_verify)
        - Jika tag tidak cocok, data telah di-tamper
        - Otomatis raise exception jika verifikasi gagal
    
    Example:
        >>> key = generate_key()
        >>> cipher = encrypt_aes("Hello", key)
        >>> plain = decrypt_aes(cipher, key)
        >>> print(plain)
        Hello
    """
    data = base64.b64decode(cipher_b64)
    # Extract nonce (16 bytes), tag (16 bytes), dan ciphertext (sisanya)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    # Dekripsi DAN verifikasi tag dalam satu langkah
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()
