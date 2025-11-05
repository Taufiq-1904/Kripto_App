"""
Clear All Messages - Database Cleanup Script
Menghapus semua pesan dari database untuk fresh start
"""

import sqlite3
import os

def clear_all_messages():
    """Hapus semua pesan dari tabel messages"""
    db_path = "secure_messenger.db"
    
    if not os.path.exists(db_path):
        print("❌ Database tidak ditemukan!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek jumlah pesan sebelum dihapus
        cursor.execute("SELECT COUNT(*) FROM messages")
        count_before = cursor.fetchone()[0]
        
        print(f"\n{'='*60}")
        print(f"  Clear All Messages")
        print(f"{'='*60}")
        print(f"Database: {db_path}")
        print(f"Total messages before: {count_before}")
        
        if count_before == 0:
            print("\n✅ Database sudah bersih, tidak ada pesan!")
            conn.close()
            return
        
        # Konfirmasi
        print(f"\n⚠️  WARNING: Ini akan menghapus {count_before} pesan!")
        confirm = input("Apakah Anda yakin? (yes/no): ")
        
        if confirm.lower() not in ['yes', 'y']:
            print("❌ Operasi dibatalkan")
            conn.close()
            return
        
        # Hapus semua pesan
        cursor.execute("DELETE FROM messages")
        conn.commit()
        
        # Reset auto increment (optional)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
        conn.commit()
        
        # Verifikasi
        cursor.execute("SELECT COUNT(*) FROM messages")
        count_after = cursor.fetchone()[0]
        
        print(f"\n✅ SUCCESS!")
        print(f"   Messages deleted: {count_before}")
        print(f"   Messages remaining: {count_after}")
        print(f"   Database bersih dan siap digunakan!")
        print(f"{'='*60}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_all_messages()
