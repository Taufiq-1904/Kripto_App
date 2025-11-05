"""
Messages Module - Modul Pengelolaan Pesan
==========================================

Module ini menangani operasi CRUD (Create, Read, Update, Delete)
untuk pesan terenkripsi dalam database.

Operasi:
- Simpan pesan baru (store)
- Ambil pesan user tertentu (fetch)
- Ambil semua pesan (fetch_all)
- Hapus pesan (delete)

Format pesan tersimpan:
    metadata::ciphertext
    - metadata: JSON berisi info algoritma dan kunci AES
    - ciphertext: Pesan terenkripsi

Security:
    - Database encryption: Semua content field dienkripsi dengan AES-256
    - Transparent encryption/decryption menggunakan db_encryption module

Author: Taufiq
Module: messages.py
"""

from db import get_connection
from db_encryption import encrypt_message_content, decrypt_message_content

def store_message(sender, receiver, content):
    """
    Simpan pesan terenkripsi ke database
    
    Args:
        sender (str): Username pengirim
        receiver (str): Username penerima
        content (str): Pesan terenkripsi (format: metadata::ciphertext)
    
    Format content:
        metadata::ciphertext
        - metadata: JSON string berisi algoritma dan kunci AES
        - ciphertext: Hasil enkripsi multi-algoritma + AES
    
    Security:
        - Content dienkripsi lagi dengan AES-256 sebelum disimpan (double encryption)
        - Menggunakan database master key
    
    Note:
        Timestamp otomatis ditambahkan oleh database (CURRENT_TIMESTAMP)
    """
    # Encrypt data before storing (database-level encryption)
    enc_sender, enc_receiver, enc_content = encrypt_message_content(sender, receiver, content)
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, receiver, content) VALUES (?, ?, ?)",
              (enc_sender, enc_receiver, enc_content))
    conn.commit()
    conn.close()

def fetch_messages(username):
    """
    Ambil semua pesan untuk user tertentu
    
    FULL ENCRYPTION MODE: Karena sender/receiver terenkripsi, kita harus:
    1. Fetch SEMUA messages dari database
    2. Decrypt semua rows
    3. Filter berdasarkan username setelah decrypt
    
    Args:
        username (str): Username yang ingin dilihat pesannya
    
    Returns:
        list: List of tuples (id, sender, receiver, content, timestamp)
              Diurutkan dari pesan terbaru ke terlama
    
    Security:
        - FULL ENCRYPTION: Sender, receiver, dan content semua terenkripsi
        - Admin tidak bisa lihat metadata di database
        - Trade-off: Performance lebih lambat (harus decrypt semua rows)
    
    Note:
        Dengan full encryption, query WHERE tidak bisa digunakan.
        Harus fetch all → decrypt → filter.
    """
    conn = get_connection()
    c = conn.cursor()
    # Fetch ALL messages (karena tidak bisa query by encrypted field)
    c.execute("""
    SELECT id, sender, receiver, content, timestamp 
    FROM messages 
    ORDER BY timestamp DESC
    """)
    rows = c.fetchall()
    conn.close()
    
    # Decrypt data after fetching dan filter by username
    decrypted_rows = []
    for row in rows:
        msg_id, sender, receiver, content, timestamp = row
        dec_sender, dec_receiver, dec_content = decrypt_message_content(sender, receiver, content)
        
        # Filter: hanya ambil pesan di mana user adalah sender ATAU receiver
        if dec_sender == username or dec_receiver == username:
            decrypted_rows.append((msg_id, dec_sender, dec_receiver, dec_content, timestamp))
    
    return decrypted_rows

def fetch_all_messages():
    """
    Ambil SEMUA pesan dalam database
    
    Fungsi ini biasanya digunakan oleh admin untuk melihat
    semua pesan dalam sistem.
    
    Returns:
        list: List of tuples (id, sender, receiver, content, timestamp)
              Diurutkan dari pesan terbaru ke terlama
    
    Security:
        - Otomatis dekripsi semua content dari database
    
    Note:
        Hanya admin yang seharusnya mengakses fungsi ini
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, sender, receiver, content, timestamp FROM messages ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    # Decrypt all data
    decrypted_rows = []
    for row in rows:
        msg_id, sender, receiver, content, timestamp = row
        dec_sender, dec_receiver, dec_content = decrypt_message_content(sender, receiver, content)
        decrypted_rows.append((msg_id, dec_sender, dec_receiver, dec_content, timestamp))
    
    return decrypted_rows

def delete_message(message_id):
    """
    Hapus pesan berdasarkan ID
    
    Args:
        message_id (int): ID pesan yang akan dihapus
    
    Warning:
        Penghapusan bersifat permanen dan tidak bisa di-undo.
        Pastikan konfirmasi user sebelum menghapus.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
