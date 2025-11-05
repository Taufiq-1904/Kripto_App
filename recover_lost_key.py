"""
Recovery Script for Lost Master Keys
Handles data migration when master keys are lost
"""

import os
import sqlite3
from datetime import datetime

def analyze_encrypted_data():
    """Analyze database untuk lihat berapa banyak data terenkripsi"""
    print("="*70)
    print("  DATABASE ENCRYPTION ANALYSIS")
    print("="*70)
    
    conn = sqlite3.connect('secure_messenger.db')
    c = conn.cursor()
    
    # Check messages
    c.execute("SELECT COUNT(*) FROM messages")
    total_messages = c.fetchone()[0]
    
    print(f"\n📊 Total Messages: {total_messages}")
    
    if total_messages > 0:
        c.execute("SELECT id, sender, receiver, content FROM messages LIMIT 5")
        messages = c.fetchall()
        
        print("\n🔍 Sample Messages (first 5):")
        for msg_id, sender, receiver, content in messages:
            # Check if encrypted (long base64 strings)
            is_encrypted = len(sender) > 30 and len(receiver) > 30
            status = "🔒 ENCRYPTED" if is_encrypted else "📖 PLAINTEXT"
            
            print(f"  ID {msg_id}: {status}")
            print(f"    Sender length: {len(sender)} chars")
            print(f"    Receiver length: {len(receiver)} chars")
            print(f"    Content length: {len(content)} chars")
    
    conn.close()

def backup_database():
    """Backup database sebelum recovery"""
    if not os.path.exists('secure_messenger.db'):
        print("❌ Database not found!")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"secure_messenger_backup_{timestamp}.db"
    
    import shutil
    shutil.copy2('secure_messenger.db', backup_file)
    
    print(f"✅ Database backed up to: {backup_file}")
    return True

def clear_encrypted_messages():
    """Clear pesan terenkripsi yang tidak bisa didekripsi"""
    print("\n" + "="*70)
    print("  CLEAR ENCRYPTED MESSAGES")
    print("="*70)
    
    print("\n⚠️  WARNING: This will delete all encrypted messages!")
    print("   (Messages that cannot be decrypted due to lost key)")
    
    response = input("\nContinue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Operation cancelled.")
        return
    
    # Backup first
    if not backup_database():
        return
    
    conn = sqlite3.connect('secure_messenger.db')
    c = conn.cursor()
    
    # Count before
    c.execute("SELECT COUNT(*) FROM messages")
    count_before = c.fetchone()[0]
    
    # Delete all messages (since we can't decrypt them)
    c.execute("DELETE FROM messages")
    
    # Reset auto-increment
    c.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
    
    conn.commit()
    
    # Count after
    c.execute("SELECT COUNT(*) FROM messages")
    count_after = c.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ Deleted {count_before - count_after} encrypted messages")
    print(f"📊 Messages remaining: {count_after}")
    print("\n🔄 You can now use the application with a new master key")
    print("   (New key will be generated automatically)")

def reset_face_recognition():
    """Reset face recognition data"""
    print("\n" + "="*70)
    print("  RESET FACE RECOGNITION")
    print("="*70)
    
    face_files = [
        "face_data/admin_faces.enc",
        "face_data/admin_model.enc"
    ]
    
    deleted = []
    for file in face_files:
        if os.path.exists(file):
            os.remove(file)
            deleted.append(file)
            print(f"✅ Deleted: {file}")
    
    if not deleted:
        print("ℹ️  No face data files found")
    else:
        print(f"\n✅ Reset complete! Deleted {len(deleted)} files")
        print("🔄 You can now re-register face authentication")
        print("   (New face_master.key will be generated)")

def check_master_keys():
    """Check status of master keys"""
    print("\n" + "="*70)
    print("  MASTER KEY STATUS")
    print("="*70)
    
    keys = {
        "db_master.key": "Database encryption",
        "face_master.key": "Face recognition encryption"
    }
    
    for key_file, description in keys.items():
        if os.path.exists(key_file):
            size = os.path.getsize(key_file)
            print(f"✅ {key_file}: PRESENT ({size} bytes)")
            print(f"   Purpose: {description}")
        else:
            print(f"❌ {key_file}: MISSING")
            print(f"   Purpose: {description}")
            print(f"   Impact: Data encrypted with this key cannot be decrypted")

def main_menu():
    """Main recovery menu"""
    print("\n" + "="*70)
    print("  MASTER KEY RECOVERY UTILITY")
    print("="*70)
    print("\n⚠️  Use this tool if you lost db_master.key or face_master.key")
    print("\nOptions:")
    print("  1. Check master key status")
    print("  2. Analyze encrypted data")
    print("  3. Clear encrypted messages (DESTRUCTIVE)")
    print("  4. Reset face recognition data")
    print("  5. Backup database")
    print("  6. Exit")
    
    while True:
        print("\n" + "-"*70)
        choice = input("Select option (1-6): ")
        
        if choice == '1':
            check_master_keys()
        elif choice == '2':
            analyze_encrypted_data()
        elif choice == '3':
            clear_encrypted_messages()
        elif choice == '4':
            reset_face_recognition()
        elif choice == '5':
            backup_database()
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option!")

if __name__ == "__main__":
    main_menu()
