"""
Quick Database Encryption Check
================================

Script untuk mengecek apakah database sudah terenkripsi atau belum.
"""

import sqlite3
import os

print("\n" + "=" * 100)
print("🔍 DATABASE ENCRYPTION CHECK")
print("=" * 100)

# Check if master key exists
print("\n[1] Checking Master Key File...")
if os.path.exists("db_master.key"):
    with open("db_master.key", "rb") as f:
        key = f.read()
    print(f"   ✅ Master key file exists: db_master.key")
    print(f"   ✅ Key length: {len(key)} bytes (expected: 16 bytes)")
    if len(key) == 16:
        print(f"   ✅ Master key is VALID!")
    else:
        print(f"   ⚠️  WARNING: Invalid key length!")
else:
    print(f"   ❌ Master key NOT found!")
    print(f"   💡 Run: python db_encryption.py to generate master key")

# Check database content
print("\n[2] Checking Database Content...")
conn = sqlite3.connect("secure_messenger.db")
c = conn.cursor()

# Count total messages
c.execute("SELECT COUNT(*) FROM messages")
total = c.fetchone()[0]
print(f"   📊 Total messages in database: {total}")

# Get sample messages
c.execute("SELECT id, sender, receiver, content FROM messages ORDER BY id DESC LIMIT 5")
rows = c.fetchall()

print("\n[3] Analyzing Last 5 Messages...")
print("=" * 100)

encrypted_count = 0
plaintext_count = 0

for row in rows:
    msg_id, sender, receiver, content = row
    
    # Check if content looks encrypted (not starting with {)
    is_encrypted = not content.startswith('{"algorithms"')
    
    if is_encrypted:
        encrypted_count += 1
        status = "✅ ENCRYPTED"
        preview = content[:60] + "..."
    else:
        plaintext_count += 1
        status = "❌ NOT ENCRYPTED"
        preview = content[:60] + "..."
    
    print(f"\nMessage ID: {msg_id} | From: {sender:12} | To: {receiver:12}")
    print(f"Status: {status}")
    print(f"Content Preview: {preview}")
    print("-" * 100)

conn.close()

# Summary
print("\n" + "=" * 100)
print("📊 SUMMARY")
print("=" * 100)
print(f"Encrypted messages:     {encrypted_count}/5")
print(f"Non-encrypted messages: {plaintext_count}/5")

if encrypted_count > 0:
    print("\n✅ DATABASE ENCRYPTION IS WORKING!")
    print("   New messages are being encrypted at rest.")
    
    if plaintext_count > 0:
        print("\n⚠️  You have OLD messages that are NOT encrypted.")
        print("   To encrypt old messages, run:")
        print("   python -c \"from db_encryption import migrate_existing_database; migrate_existing_database()\"")
else:
    print("\n❌ DATABASE ENCRYPTION IS NOT WORKING!")
    print("   All messages are stored in plaintext.")
    print("\n💡 Troubleshooting:")
    print("   1. Check if db_encryption.py exists")
    print("   2. Check if messages.py imports db_encryption")
    print("   3. Restart the application")

print("\n" + "=" * 100)
print("🔐 How to Verify Encryption Manually:")
print("=" * 100)
print("""
1. Open database with SQLite Browser or command line
2. Look at 'messages' table, 'content' column
3. Encrypted data looks like: "9685G8o+k/J1c+yUN7TQ..."
4. Non-encrypted data looks like: {"algorithms": ["vigenere"...

If you see random base64 strings → ✅ ENCRYPTED
If you see JSON with "algorithms" → ❌ NOT ENCRYPTED
""")

print("=" * 100)
print("✅ Check complete!")
print("=" * 100 + "\n")
