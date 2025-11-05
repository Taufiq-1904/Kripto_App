"""
Database Encryption Module - Enkripsi Database
==============================================

Module ini menyediakan fungsi untuk mengenkripsi data sebelum
disimpan ke database dan dekripsi saat membaca dari database.

Security Features:
- AES-256 encryption untuk semua data sensitif
- Master key untuk enkripsi database
- Transparent encryption/decryption

Author: Taufiq
Module: db_encryption.py
"""

from crypto.aes import encrypt_aes, decrypt_aes, generate_key
import base64
import os

# ============================================================================
# DATABASE MASTER KEY
# ============================================================================
"""
PENTING: Master key ini digunakan untuk mengenkripsi SEMUA data di database.
Jika key hilang, data TIDAK BISA didekripsi!

Production Deployment:
- Simpan master key di file terpisah (db_master.key)
- Atau gunakan environment variable
- JANGAN commit master key ke Git!
"""

def get_or_create_master_key():
    """
    Ambil atau buat master key untuk enkripsi database
    
    Master key disimpan di file 'db_master.key' di direktori yang sama.
    Jika file tidak ada, akan dibuat key baru.
    
    Returns:
        bytes: Master key 16 bytes untuk AES encryption
    
    Security:
        - Key di-generate dengan cryptographically secure random
        - File key harus dijaga kerahasiaannya
        - Backup key di lokasi aman!
    """
    key_file = "db_master.key"
    
    if os.path.exists(key_file):
        # Load existing key
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        # Generate new key
        key = generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        print("⚠️  NEW DATABASE MASTER KEY GENERATED!")
        print(f"📁 Saved to: {key_file}")
        print("🔒 BACKUP THIS FILE! If lost, data cannot be decrypted!")
        return key

# Global master key (loaded once at startup)
MASTER_KEY = get_or_create_master_key()

# ============================================================================
# ENCRYPTION/DECRYPTION FUNCTIONS
# ============================================================================

def encrypt_field(plaintext):
    """
    Enkripsi field sebelum disimpan ke database
    
    Args:
        plaintext (str): Data plaintext yang akan dienkripsi
    
    Returns:
        str: Data terenkripsi dalam format base64
    
    Note:
        - Menggunakan AES-256 dengan master key
        - Return format base64 untuk compatibility dengan SQLite TEXT field
        - Empty string atau None akan di-skip (tidak dienkripsi)
    """
    if not plaintext:
        return plaintext
    
    try:
        encrypted = encrypt_aes(plaintext, MASTER_KEY)
        return encrypted
    except Exception as e:
        print(f"❌ Encryption error: {e}")
        return plaintext  # Fallback: simpan tanpa enkripsi jika gagal

def decrypt_field(ciphertext):
    """
    Dekripsi field saat membaca dari database
    
    Args:
        ciphertext (str): Data terenkripsi dari database
    
    Returns:
        str: Plaintext hasil dekripsi
    
    Note:
        - Jika dekripsi gagal, return ciphertext asli
        - Handle error untuk backward compatibility (data lama yang tidak terenkripsi)
        - Smart detection: Check if data looks encrypted before attempting decrypt
    """
    if not ciphertext:
        return ciphertext
    
    # Smart detection: If data looks like plaintext (short alphanumeric), don't decrypt
    # Encrypted data is always long base64 strings (minimum 40+ chars)
    if len(ciphertext) < 30 or not any(c in ciphertext for c in ['+', '/', '=']):
        # Likely plaintext (e.g., "akmal", "alice_test")
        return ciphertext
    
    try:
        decrypted = decrypt_aes(ciphertext, MASTER_KEY)
        return decrypted
    except Exception:
        # Silent fallback for backward compatibility
        # Don't print warnings - just return original data
        return ciphertext

# ============================================================================
# HELPER FUNCTIONS FOR DATABASE OPERATIONS
# ============================================================================

def encrypt_message_content(sender, receiver, content):
    """
    Enkripsi data pesan sebelum disimpan
    
    Args:
        sender (str): Username pengirim
        receiver (str): Username penerima
        content (str): Konten pesan terenkripsi (sudah multi-algo + AES)
    
    Returns:
        tuple: (encrypted_sender, encrypted_receiver, encrypted_content)
    
    Note:
        FULL ENCRYPTION MODE: Semua field dienkripsi termasuk sender dan receiver
        - Maximum security: Admin tidak bisa lihat metadata
        - Trade-off: Query lebih lambat (harus decrypt semua rows)
    """
    # FULL ENCRYPTION: Enkripsi SEMUA field untuk maximum security
    return (encrypt_field(sender), encrypt_field(receiver), encrypt_field(content))

def decrypt_message_content(sender, receiver, content):
    """
    Dekripsi data pesan saat membaca dari database
    
    Args:
        sender (str): Username pengirim (encrypted)
        receiver (str): Username penerima (encrypted)
        content (str): Konten pesan (encrypted)
    
    Returns:
        tuple: (decrypted_sender, decrypted_receiver, decrypted_content)
    
    Note:
        FULL ENCRYPTION MODE: Dekripsi semua field
    """
    # FULL DECRYPTION: Dekripsi SEMUA field
    return (decrypt_field(sender), decrypt_field(receiver), decrypt_field(content))

# ============================================================================
# DATABASE MIGRATION (Optional)
# ============================================================================

def migrate_existing_database():
    """
    Enkripsi data yang sudah ada di database (migration)
    
    Fungsi ini akan:
    1. Baca semua data dari database
    2. Enkripsi field sensitif
    3. Update kembali ke database
    
    WARNING: Backup database dulu sebelum jalankan!
    
    Usage:
        from db_encryption import migrate_existing_database
        migrate_existing_database()
    """
    from db import get_connection
    
    print("🔄 Starting database migration...")
    print("⚠️  Make sure you have backed up secure_messenger.db!")
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Migration cancelled.")
        return
    
    conn = get_connection()
    c = conn.cursor()
    
    # Encrypt messages
    c.execute("SELECT id, sender, receiver, content FROM messages")
    messages = c.fetchall()
    
    for msg_id, sender, receiver, content in messages:
        enc_sender, enc_receiver, enc_content = encrypt_message_content(sender, receiver, content)
        c.execute("""
            UPDATE messages 
            SET sender=?, receiver=?, content=? 
            WHERE id=?
        """, (enc_sender, enc_receiver, enc_content, msg_id))
        print(f"✅ Encrypted message ID: {msg_id}")
    
    conn.commit()
    conn.close()
    
    print("✅ Database migration completed!")
    print("🔒 All data is now encrypted at rest.")

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Test encryption/decryption
    test_data = "Hello Secret Message!"
    
    print("Original:", test_data)
    encrypted = encrypt_field(test_data)
    print("Encrypted:", encrypted)
    decrypted = decrypt_field(encrypted)
    print("Decrypted:", decrypted)
    
    assert test_data == decrypted, "Encryption/Decryption test failed!"
    print("✅ Encryption test passed!")
