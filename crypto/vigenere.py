"""
Vigenère Cipher Module - Modul Cipher Vigenère
===============================================

Module ini mengimplementasikan Vigenère cipher, salah satu cipher
klasik yang menggunakan polyalphabetic substitution.

Vigenère Cipher:
- Menggunakan kunci berupa kata/frasa
- Setiap huruf di-shift berdasarkan huruf kunci
- Kunci diulang jika lebih pendek dari plaintext
- Lebih kuat dari Caesar cipher (tidak bisa dipecah dengan frequency analysis)

History:
- Ditemukan oleh Giovan Battista Bellaso (1553)
- Dinamai dari Blaise de Vigenère
- Disebut "le chiffre indéchiffrable" (the unbreakable cipher)

Author: Taufiq
Module: crypto/vigenere.py
"""

def vigenere_encrypt(text, key):
    """
    Enkripsi teks menggunakan Vigenère cipher
    
    Setiap huruf dalam plaintext di-shift berdasarkan huruf yang sesuai
    dalam kunci. Kunci diulang jika lebih pendek dari teks.
    
    Args:
        text (str): Plaintext yang akan dienkripsi
        key (str): Kunci enkripsi (kata/frasa)
    
    Returns:
        str: Ciphertext
    
    Cara Kerja:
        1. Konversi kunci ke uppercase
        2. Untuk setiap huruf di plaintext:
           - Ambil huruf kunci yang sesuai (dengan modulo)
           - Shift huruf plaintext sebanyak nilai huruf kunci (A=0, B=1, ..., Z=25)
        3. Huruf non-alfabet tidak dienkripsi
    
    Example:
        >>> vigenere_encrypt("HELLO", "KEY")
        'RIJVS'
        
        Penjelasan:
        H + K = H(7) + K(10) = R(17)
        E + E = E(4) + E(4)  = I(8)
        L + Y = L(11) + Y(24) = J(9)
        L + K = L(11) + K(10) = V(21)
        O + E = O(14) + E(4)  = S(18)
    """
    result = []
    key = key.upper()  # Standardisasi kunci ke uppercase
    
    for i, char in enumerate(text):
        if char.isalpha():
            # Hitung shift dari huruf kunci (A=0, B=1, ..., Z=25)
            shift = ord(key[i % len(key)]) - 65
            
            if char.isupper():
                # Enkripsi huruf besar
                result.append(chr((ord(char) + shift - 65) % 26 + 65))
            else:
                # Enkripsi huruf kecil
                result.append(chr((ord(char) + shift - 97) % 26 + 97))
        else:
            # Karakter non-alfabet tidak diubah
            result.append(char)
    
    return ''.join(result)

def vigenere_decrypt(cipher, key):
    """
    Dekripsi ciphertext Vigenère
    
    Kebalikan dari enkripsi - shift mundur berdasarkan huruf kunci.
    
    Args:
        cipher (str): Ciphertext yang akan didekripsi
        key (str): Kunci yang sama dengan saat enkripsi
    
    Returns:
        str: Plaintext asli
    
    Cara Kerja:
        Sama dengan enkripsi, tapi shift mundur (dikurangi)
    
    Example:
        >>> vigenere_decrypt("RIJVS", "KEY")
        'HELLO'
    
    Note:
        Kunci harus PERSIS sama dengan saat enkripsi.
        Case-insensitive (KEY = key = KeY)
    """
    result = []
    key = key.upper()
    
    for i, char in enumerate(cipher):
        if char.isalpha():
            # Hitung shift dari huruf kunci
            shift = ord(key[i % len(key)]) - 65
            
            if char.isupper():
                # Dekripsi huruf besar (shift mundur)
                result.append(chr((ord(char) - shift - 65) % 26 + 65))
            else:
                # Dekripsi huruf kecil (shift mundur)
                result.append(chr((ord(char) - shift - 97) % 26 + 97))
        else:
            # Karakter non-alfabet tidak diubah
            result.append(char)
    
    return ''.join(result)
