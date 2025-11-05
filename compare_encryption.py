"""
Visual Comparison: Partial vs Full Encryption
==============================================
"""
import sqlite3

conn = sqlite3.connect('secure_messenger.db')
c = conn.cursor()

# Fetch all messages
c.execute("""
    SELECT id, sender, receiver, content 
    FROM messages 
    ORDER BY id
""")
rows = c.fetchall()
conn.close()

print("\n" + "=" * 100)
print("🔍 VISUAL COMPARISON: Partial Encryption vs Full Encryption")
print("=" * 100)

# Show old messages (partial encryption)
print("\n📊 OLD MESSAGES (Partial Encryption - Content Only):")
print("-" * 100)
print("Sender & Receiver are READABLE, only Content is encrypted\n")

for row in rows[:3]:
    msg_id, sender, receiver, content = row
    print(f"ID: {msg_id}")
    print(f"  Sender:   {sender:20} ← PLAINTEXT (anyone can read!)")
    print(f"  Receiver: {receiver:20} ← PLAINTEXT (anyone can read!)")
    print(f"  Content:  {content[:60]}... ← Encrypted")
    print("-" * 100)

# Show new messages (full encryption)
print("\n🔐 NEW MESSAGES (FULL ENCRYPTION - ALL Fields):")
print("-" * 100)
print("Sender, Receiver, AND Content are ALL ENCRYPTED\n")

for row in rows[5:]:
    msg_id, sender, receiver, content = row
    print(f"ID: {msg_id}")
    print(f"  Sender:   {sender[:60]}... ← ENCRYPTED!")
    print(f"  Receiver: {receiver[:60]}... ← ENCRYPTED!")
    print(f"  Content:  {content[:60]}... ← ENCRYPTED!")
    print("-" * 100)

print("\n" + "=" * 100)
print("📈 SUMMARY:")
print("=" * 100)
print("""
OLD APPROACH (Partial Encryption):
  ❌ Sender:   Readable → Admin dapat lihat "akmal", "alice_test", etc
  ❌ Receiver: Readable → Admin dapat lihat siapa berkomunikasi dengan siapa
  ✅ Content:  Encrypted → Isi pesan aman

NEW APPROACH (FULL Encryption):
  ✅ Sender:   ENCRYPTED → Admin hanya lihat gibberish
  ✅ Receiver: ENCRYPTED → Metadata komunikasi tersembunyi
  ✅ Content:  ENCRYPTED → Isi pesan aman

🔒 BENEFIT OF FULL ENCRYPTION:
  • Admin TIDAK bisa lihat siapa mengirim pesan
  • Admin TIDAK bisa lihat siapa menerima pesan
  • Admin TIDAK bisa lihat metadata komunikasi
  • Admin TIDAK bisa lihat isi pesan
  • Maximum privacy & security!

⚠️  TRADE-OFF:
  • Query lebih lambat (harus decrypt semua rows untuk filter)
  • Tidak bisa search by sender/receiver di database level
  • Semua filtering dilakukan setelah decryption di aplikasi
""")
print("=" * 100)
