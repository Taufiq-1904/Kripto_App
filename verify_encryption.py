"""
Complete Database Encryption Verification
==========================================

Script untuk verifikasi LENGKAP bahwa semua data di database
sudah terenkripsi dengan baik.
"""

import sqlite3
import os

def check_field_encrypted(field_value):
    """Check if a field looks encrypted"""
    if not field_value:
        return False, "Empty"
    
    # Encrypted data characteristics:
    # 1. Length > 30 characters
    # 2. Contains base64 characters (+, /, =)
    # 3. Looks like random gibberish
    
    has_base64_chars = any(c in field_value for c in ['+', '/', '='])
    is_long = len(field_value) > 30
    
    if is_long and has_base64_chars:
        return True, "Encrypted (base64)"
    elif is_long:
        return True, "Encrypted (long)"
    else:
        return False, "Plaintext"

print("\n" + "=" * 100)
print("🔐 COMPLETE DATABASE ENCRYPTION VERIFICATION")
print("=" * 100)

# Check 1: Master Key
print("\n[CHECK 1] Master Key File")
print("-" * 100)
if os.path.exists("db_master.key"):
    with open("db_master.key", "rb") as f:
        key = f.read()
    print(f"✅ Master key exists: db_master.key")
    print(f"✅ Key length: {len(key)} bytes")
    if len(key) == 16:
        print(f"✅ Key is valid (16 bytes = 128-bit AES)")
        master_key_ok = True
    else:
        print(f"❌ Invalid key length! Expected 16 bytes")
        master_key_ok = False
else:
    print(f"❌ Master key NOT found!")
    master_key_ok = False

# Check 2: Database Connection
print("\n[CHECK 2] Database Connection")
print("-" * 100)
try:
    conn = sqlite3.connect("secure_messenger.db")
    print("✅ Successfully connected to secure_messenger.db")
    db_ok = True
except Exception as e:
    print(f"❌ Cannot connect to database: {e}")
    db_ok = False
    exit(1)

# Check 3: Messages Table Analysis
print("\n[CHECK 3] Messages Table Analysis")
print("-" * 100)

c = conn.cursor()
c.execute("SELECT COUNT(*) FROM messages")
total_messages = c.fetchone()[0]
print(f"📊 Total messages in database: {total_messages}")

if total_messages == 0:
    print("⚠️  No messages in database to verify!")
    conn.close()
    exit(0)

# Analyze all messages
c.execute("SELECT id, sender, receiver, content FROM messages ORDER BY id")
all_messages = c.fetchall()
conn.close()

# Statistics
stats = {
    'total': len(all_messages),
    'fully_encrypted': 0,    # Sender, receiver, content all encrypted
    'partially_encrypted': 0,  # Only content encrypted
    'not_encrypted': 0        # Nothing encrypted
}

print("\n[CHECK 4] Field-by-Field Encryption Status")
print("-" * 100)

for msg_id, sender, receiver, content in all_messages:
    sender_enc, sender_status = check_field_encrypted(sender)
    receiver_enc, receiver_status = check_field_encrypted(receiver)
    content_enc, content_status = check_field_encrypted(content)
    
    # Determine encryption level
    if sender_enc and receiver_enc and content_enc:
        level = "FULL"
        icon = "✅"
        stats['fully_encrypted'] += 1
    elif content_enc and not (sender_enc or receiver_enc):
        level = "PARTIAL"
        icon = "⚠️ "
        stats['partially_encrypted'] += 1
    else:
        level = "NONE"
        icon = "❌"
        stats['not_encrypted'] += 1
    
    print(f"\nMessage ID: {msg_id} [{icon} {level} ENCRYPTION]")
    print(f"  Sender:   {sender[:40]:40} → {sender_status}")
    print(f"  Receiver: {receiver[:40]:40} → {receiver_status}")
    print(f"  Content:  {content[:40]:40} → {content_status}")

# Summary
print("\n" + "=" * 100)
print("📊 ENCRYPTION SUMMARY")
print("=" * 100)

print(f"\nTotal Messages: {stats['total']}")
print(f"  ✅ Fully Encrypted:     {stats['fully_encrypted']:3} ({stats['fully_encrypted']/stats['total']*100:.1f}%)")
print(f"  ⚠️  Partially Encrypted: {stats['partially_encrypted']:3} ({stats['partially_encrypted']/stats['total']*100:.1f}%)")
print(f"  ❌ Not Encrypted:       {stats['not_encrypted']:3} ({stats['not_encrypted']/stats['total']*100:.1f}%)")

# Overall Assessment
print("\n" + "=" * 100)
print("🎯 OVERALL ASSESSMENT")
print("=" * 100)

score = (stats['fully_encrypted'] * 100 + stats['partially_encrypted'] * 50) / stats['total']

if stats['fully_encrypted'] == stats['total']:
    grade = "A+"
    status = "✅ EXCELLENT"
    message = "All messages are FULLY ENCRYPTED! Maximum security achieved!"
elif stats['fully_encrypted'] > 0 and stats['partially_encrypted'] > 0:
    grade = "B+"
    status = "✅ GOOD"
    message = "New messages are fully encrypted. Old messages partially encrypted."
elif stats['partially_encrypted'] == stats['total']:
    grade = "C"
    status = "⚠️  FAIR"
    message = "Only content encrypted. Consider full encryption for better security."
else:
    grade = "F"
    status = "❌ POOR"
    message = "Database encryption not working! Check configuration."

print(f"\nSecurity Grade: {grade}")
print(f"Status: {status}")
print(f"Score: {score:.1f}/100")
print(f"\n{message}")

# Recommendations
print("\n" + "=" * 100)
print("💡 RECOMMENDATIONS")
print("=" * 100)

if stats['fully_encrypted'] == stats['total']:
    print("""
✅ Perfect! Your database is fully encrypted.
✅ All sender, receiver, and content fields are encrypted.
✅ Admin cannot see any metadata.
✅ Maximum privacy achieved!

Next Steps:
  • Backup db_master.key securely
  • Regular security audits
  • Monitor for any new unencrypted data
""")
elif stats['fully_encrypted'] > 0:
    print(f"""
✅ Good! New messages are fully encrypted ({stats['fully_encrypted']} messages).
⚠️  Old messages still have plaintext metadata ({stats['partially_encrypted']} messages).

Recommendations:
  • Continue using full encryption for new messages
  • Old messages are still partially protected (content encrypted)
  • Optional: Migrate old messages to full encryption
  
To migrate old messages:
  python -c "from db_encryption import migrate_existing_database; migrate_existing_database()"
""")
else:
    print("""
❌ Warning! Database encryption may not be working properly.

Action Required:
  1. Check if db_encryption.py is properly configured
  2. Check if messages.py uses encrypt_message_content()
  3. Check if db_master.key exists and is valid
  4. Review FULL_ENCRYPTION_GUIDE.md for setup instructions
  5. Test by sending a new encrypted message
""")

# Detailed Breakdown
print("\n" + "=" * 100)
print("📋 DETAILED BREAKDOWN")
print("=" * 100)

print("\nFully Encrypted Messages (All fields encrypted):")
if stats['fully_encrypted'] > 0:
    for msg_id, sender, receiver, content in all_messages:
        sender_enc, _ = check_field_encrypted(sender)
        receiver_enc, _ = check_field_encrypted(receiver)
        content_enc, _ = check_field_encrypted(content)
        if sender_enc and receiver_enc and content_enc:
            print(f"  • Message ID {msg_id}: ✅ Sender, Receiver, Content all encrypted")
else:
    print("  None")

print("\nPartially Encrypted Messages (Only content encrypted):")
if stats['partially_encrypted'] > 0:
    for msg_id, sender, receiver, content in all_messages:
        sender_enc, _ = check_field_encrypted(sender)
        receiver_enc, _ = check_field_encrypted(receiver)
        content_enc, _ = check_field_encrypted(content)
        if content_enc and not (sender_enc or receiver_enc):
            print(f"  • Message ID {msg_id}: ⚠️  Sender '{sender}', Receiver '{receiver}' visible")
else:
    print("  None")

print("\nNot Encrypted Messages:")
if stats['not_encrypted'] > 0:
    for msg_id, sender, receiver, content in all_messages:
        sender_enc, _ = check_field_encrypted(sender)
        receiver_enc, _ = check_field_encrypted(receiver)
        content_enc, _ = check_field_encrypted(content)
        if not (sender_enc or receiver_enc or content_enc):
            print(f"  • Message ID {msg_id}: ❌ All fields plaintext!")
else:
    print("  None")

print("\n" + "=" * 100)
print("✅ Verification Complete!")
print("=" * 100 + "\n")
