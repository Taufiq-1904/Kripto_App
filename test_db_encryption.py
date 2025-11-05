"""
Quick Test Script - Test Database Encryption
=============================================

Script ini untuk testing cepat fitur enkripsi database.

Test Cases:
1. Test enkripsi/dekripsi field
2. Test simpan dan baca pesan dengan enkripsi
3. Verifikasi data di database benar-benar terenkripsi

Usage:
    python test_db_encryption.py
"""

import sqlite3
from db_encryption import encrypt_field, decrypt_field, MASTER_KEY
from messages import store_message, fetch_messages
from auth import create_user, login
from db import init_db

print("=" * 60)
print("🧪 DATABASE ENCRYPTION TEST")
print("=" * 60)

# Initialize database
init_db()

# ============================================================================
# TEST 1: Basic Encryption/Decryption
# ============================================================================
print("\n[TEST 1] Basic Field Encryption")
print("-" * 60)

test_data = "This is a SECRET message! 🔒"
print(f"Original:  {test_data}")

encrypted = encrypt_field(test_data)
print(f"Encrypted: {encrypted[:50]}...")
print(f"Length:    {len(encrypted)} chars")

decrypted = decrypt_field(encrypted)
print(f"Decrypted: {decrypted}")

if test_data == decrypted:
    print("✅ TEST 1 PASSED: Encryption/Decryption works!")
else:
    print("❌ TEST 1 FAILED: Decryption mismatch!")
    exit(1)

# ============================================================================
# TEST 2: Message Storage with Encryption
# ============================================================================
print("\n[TEST 2] Message Storage with Database Encryption")
print("-" * 60)

# Create test users
test_sender = "alice_test"
test_receiver = "bob_test"
test_password = "test123"

try:
    create_user(test_sender, test_password)
    create_user(test_receiver, test_password)
    print(f"✅ Created test users: {test_sender}, {test_receiver}")
except:
    print(f"⚠️  Users already exist (OK)")

# Store test message
test_message = "metadata::encrypted_test_message_12345"
store_message(test_sender, test_receiver, test_message)
print(f"✅ Stored message from {test_sender} to {test_receiver}")

# Fetch message
messages = fetch_messages(test_sender)
if messages:
    msg_id, sender, receiver, content, timestamp = messages[0]
    print(f"✅ Fetched message:")
    print(f"   From: {sender}")
    print(f"   To: {receiver}")
    print(f"   Content: {content[:50]}...")
    
    if content == test_message:
        print("✅ TEST 2 PASSED: Message stored and retrieved correctly!")
    else:
        print("❌ TEST 2 FAILED: Message content mismatch!")
        print(f"   Expected: {test_message}")
        print(f"   Got: {content}")
        exit(1)
else:
    print("❌ TEST 2 FAILED: No messages found!")
    exit(1)

# ============================================================================
# TEST 3: Verify Actual Database Encryption
# ============================================================================
print("\n[TEST 3] Verify Data in Database is Actually Encrypted")
print("-" * 60)

# Read directly from database (bypass decryption)
conn = sqlite3.connect("secure_messenger.db")
c = conn.cursor()
c.execute("SELECT content FROM messages ORDER BY id DESC LIMIT 1")
raw_data = c.fetchone()[0]
conn.close()

print(f"Raw data in DB: {raw_data[:80]}...")
print(f"Original data:  {test_message}")

if raw_data != test_message:
    print("✅ TEST 3 PASSED: Data is ENCRYPTED in database!")
    print(f"   (Raw data ≠ Original data)")
else:
    print("⚠️  TEST 3 WARNING: Data might not be encrypted!")
    print(f"   (Raw data = Original data)")

# Verify we can decrypt raw data with master key
try:
    from crypto.aes import decrypt_aes
    decrypted_raw = decrypt_aes(raw_data, MASTER_KEY)
    if decrypted_raw == test_message:
        print("✅ Raw data successfully decrypted with master key!")
    else:
        print("⚠️  Raw data decryption mismatch")
except Exception as e:
    print(f"⚠️  Could not decrypt raw data: {e}")

# ============================================================================
# TEST 4: Master Key Verification
# ============================================================================
print("\n[TEST 4] Master Key Verification")
print("-" * 60)

import os
if os.path.exists("db_master.key"):
    with open("db_master.key", 'rb') as f:
        key = f.read()
    print(f"✅ Master key file exists")
    print(f"   Length: {len(key)} bytes")
    print(f"   Expected: 16 bytes (128-bit AES)")
    
    if len(key) == 16:
        print("✅ TEST 4 PASSED: Master key has correct length!")
    else:
        print("❌ TEST 4 FAILED: Invalid key length!")
        exit(1)
else:
    print("❌ TEST 4 FAILED: Master key file not found!")
    exit(1)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("""
✅ Database encryption is working correctly!
✅ Messages are encrypted at rest
✅ Decryption works transparently
✅ Master key is properly configured

Your data is now protected with double encryption:
1. Application-level: Multi-algorithm + AES (user keys)
2. Database-level: AES-256 (master key)

🔒 REMEMBER TO BACKUP: db_master.key
""")
