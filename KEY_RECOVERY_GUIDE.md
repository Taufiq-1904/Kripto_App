# 🚨 PANDUAN: KEHILANGAN MASTER KEYS

## Skenario: db_master.key dan/atau face_master.key HILANG

---

## 📋 DAFTAR ISI
1. [Dampak Kehilangan](#dampak-kehilangan)
2. [Recovery Options](#recovery-options)
3. [Prevention Strategies](#prevention-strategies)
4. [Step-by-Step Recovery](#step-by-step-recovery)

---

## 🔴 DAMPAK KEHILANGAN

### **Kehilangan `db_master.key`**

#### ❌ **Data yang HILANG PERMANEN:**
- **Semua pesan terenkripsi** di database
- **Metadata pesan** (sender/receiver)
- **Konten pesan** yang sudah dikirim/diterima

#### ✅ **Data yang MASIH AMAN:**
- User accounts (username)
- Password hashes (tidak butuh db_master.key)
- Login sistem masih berfungsi
- Database structure intact

#### 💥 **Error yang Muncul:**
```
❌ Saat buka inbox: "Failed to decrypt message"
❌ Saat kirim pesan: Akan dienkripsi dengan key BARU
❌ Pesan lama: TIDAK BISA dibaca (encrypted dengan key lama)
```

---

### **Kehilangan `face_master.key`**

#### ❌ **Fungsi yang TIDAK BISA DIPAKAI:**
- Face recognition login
- Load model LBPH yang sudah ditraining
- Lihat face samples yang sudah di-capture

#### ✅ **Fungsi yang MASIH BISA DIPAKAI:**
- Login dengan username/password
- Semua fitur aplikasi lainnya
- Re-register face baru (key baru akan di-generate)

#### 💥 **Error yang Muncul:**
```
❌ Face login: "No admin face found" atau "Failed to load model"
✅ Solution: Re-register face baru
```

---

### **Kehilangan KEDUA Keys**

#### 🚨 **CRITICAL SITUATION:**
- Database messages: **HILANG**
- Face authentication: **TIDAK BERFUNGSI**
- Recovery: **PARTIAL** (hanya face bisa di-recover)

---

## 🛠️ RECOVERY OPTIONS

### **OPTION 1: Restore dari Backup** ⭐ (RECOMMENDED)

#### **Jika Anda PUNYA backup keys:**

```powershell
# 1. Copy keys dari backup location
Copy-Item "E:\Backup\db_master.key" ".\db_master.key"
Copy-Item "E:\Backup\face_master.key" ".\face_master.key"

# 2. Verify keys
Get-ChildItem *_master.key | Select-Object Name, Length

# 3. Restart aplikasi
python main.py

# 4. Test functionality
# - Buka inbox (should work)
# - Face login (should work)
```

**Result**: ✅ **100% RECOVERY - Semua data kembali!**

---

### **OPTION 2: Generate Key Baru** ⚠️ (DATA LOSS)

#### **Jika Anda TIDAK PUNYA backup:**

#### **A. Recovery untuk Database**

**Konsekuensi:**
- ❌ Pesan lama: **HILANG PERMANEN**
- ✅ Pesan baru: Bisa dienkripsi dengan key baru
- ✅ User accounts: Tetap ada

**Steps:**

```powershell
# 1. Jalankan recovery utility
python recover_lost_key.py

# Menu akan muncul:
# Select option: 3 (Clear encrypted messages)

# 2. Backup database akan otomatis dibuat
# 3. Encrypted messages akan dihapus
# 4. Restart aplikasi - key baru otomatis generated

# 5. Verify
python main.py
# - Login: ✅ Works
# - Send new message: ✅ Works (with new key)
# - Read old messages: ❌ Gone
```

#### **B. Recovery untuk Face Recognition**

**Konsekuensi:**
- ❌ Face data lama: **HILANG**
- ✅ Face recognition: Bisa digunakan lagi (dengan re-register)

**Steps:**

```powershell
# 1. Jalankan recovery utility
python recover_lost_key.py

# Menu:
# Select option: 4 (Reset face recognition)

# 2. File .enc akan dihapus
# 3. Restart aplikasi
python main.py

# 4. Login dengan username/password
# 5. Re-register face di Admin Panel
# - Klik "🔄 Re-register Face"
# - face_master.key baru akan di-generate
# - Capture wajah baru
```

**Result**: ✅ **Face authentication works again!**

---

### **OPTION 3: Manual Recovery**

#### **Untuk Advanced Users:**

```python
# 1. Backup database
import shutil
shutil.copy2('secure_messenger.db', 'backup.db')

# 2. Delete key files (if corrupted)
import os
if os.path.exists('db_master.key'):
    os.remove('db_master.key')

# 3. Run application
# System akan generate key baru otomatis

# 4. Clear old encrypted data
import sqlite3
conn = sqlite3.connect('secure_messenger.db')
c = conn.cursor()
c.execute("DELETE FROM messages")
conn.commit()
conn.close()

# 5. Start fresh dengan key baru
```

---

## 🛡️ PREVENTION STRATEGIES

### **1. Automated Backup** 🔄

**Setup script backup otomatis:**

```powershell
# backup_keys.ps1
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "E:\Backup\Kripto_App\$timestamp"
New-Item -ItemType Directory -Path $backupDir -Force

Copy-Item "db_master.key" "$backupDir\db_master.key"
Copy-Item "face_master.key" "$backupDir\face_master.key"
Copy-Item "secure_messenger.db" "$backupDir\secure_messenger.db"

Write-Host "✅ Backup complete: $backupDir"
```

**Schedule dengan Task Scheduler:**
- Frequency: Daily
- Time: 2:00 AM
- Location: External drive atau cloud

---

### **2. Multiple Backup Locations** 📍

Simpan backup di **3 lokasi berbeda:**

1. **Local External Drive** (USB/External HDD)
   ```
   E:\Backup\Kripto_App\
   ```

2. **Cloud Storage** (OneDrive/Google Drive)
   ```
   OneDrive\Kripto_App_Backup\
   ```

3. **Password Manager** (1Password/Bitwarden)
   - Upload keys sebagai secure files
   - Add notes dengan recovery instructions

---

### **3. Key Export Feature** 📤

**Tambahkan di aplikasi:**

```python
def export_keys():
    """Export keys untuk backup"""
    import tkinter.filedialog as fd
    
    backup_dir = fd.askdirectory(title="Select backup location")
    if backup_dir:
        shutil.copy2('db_master.key', f'{backup_dir}/db_master.key')
        shutil.copy2('face_master.key', f'{backup_dir}/face_master.key')
        messagebox.showinfo("Success", f"Keys backed up to:\n{backup_dir}")
```

Tambahkan button di Admin Panel:
```
💾 Export Encryption Keys
```

---

### **4. Key Recovery Code** 🔑

**Generate recovery code dari key:**

```python
import base64

def generate_recovery_code(key_file):
    """Generate human-readable recovery code"""
    with open(key_file, 'rb') as f:
        key = f.read()
    
    # Encode to base64
    code = base64.b64encode(key).decode()
    
    # Format as groups (easier to type)
    formatted = '-'.join([code[i:i+4] for i in range(0, len(code), 4)])
    
    return formatted

# Example output:
# db_master.key recovery code:
# xJ8k-2P9L-3mQ7-TpYz-N7u8-9xK2
```

User bisa simpan code ini di tempat aman (paper backup).

---

### **5. Key Integrity Check** ✅

**Verify keys secara berkala:**

```python
def verify_keys():
    """Check if keys are valid and functional"""
    
    # Check db_master.key
    try:
        with open('db_master.key', 'rb') as f:
            db_key = f.read()
        
        if len(db_key) != 16:
            alert("⚠️ db_master.key corrupted!")
        else:
            print("✅ db_master.key OK")
    except:
        alert("❌ db_master.key MISSING!")
    
    # Check face_master.key
    try:
        with open('face_master.key', 'rb') as f:
            face_key = f.read()
        
        if len(face_key) != 16:
            alert("⚠️ face_master.key corrupted!")
        else:
            print("✅ face_master.key OK")
    except:
        alert("❌ face_master.key MISSING!")
```

Run check ini:
- At startup
- Weekly automatic check
- After system crash

---

## 📖 STEP-BY-STEP RECOVERY

### **Scenario A: Lost db_master.key**

1. **Cek backup:**
   ```powershell
   Get-ChildItem "E:\Backup\Kripto_App\" -Recurse | Where {$_.Name -eq "db_master.key"}
   ```

2. **Jika ada backup:**
   ```powershell
   Copy-Item "E:\Backup\...\db_master.key" ".\db_master.key"
   python main.py  # Test
   ```

3. **Jika TIDAK ada backup:**
   ```powershell
   python recover_lost_key.py
   # Option 3: Clear encrypted messages
   # Confirm: yes
   ```

4. **Verify recovery:**
   - Login ✅
   - Send new message ✅
   - Old messages ❌ (gone)

---

### **Scenario B: Lost face_master.key**

1. **Cek backup:**
   ```powershell
   Get-ChildItem "E:\Backup\Kripto_App\" -Recurse | Where {$_.Name -eq "face_master.key"}
   ```

2. **Jika ada backup:**
   ```powershell
   Copy-Item "E:\Backup\...\face_master.key" ".\face_master.key"
   python main.py  # Test face login
   ```

3. **Jika TIDAK ada backup:**
   ```powershell
   python recover_lost_key.py
   # Option 4: Reset face recognition
   python main.py
   # Re-register face di Admin Panel
   ```

4. **Verify recovery:**
   - Face login ✅ (after re-register)
   - Face model ✅ (new)

---

### **Scenario C: Lost BOTH keys**

1. **Prioritas:**
   - Database key > Face key (data lebih penting)

2. **Check backups:**
   ```powershell
   Get-ChildItem "E:\Backup\Kripto_App\" -Recurse | Where {$_.Name -like "*master.key"}
   ```

3. **Recovery:**
   ```powershell
   # Restore both if available
   Copy-Item "E:\Backup\...\db_master.key" "."
   Copy-Item "E:\Backup\...\face_master.key" "."
   
   # OR use recovery utility
   python recover_lost_key.py
   # Option 3: Clear messages
   # Option 4: Reset face
   ```

---

## ⚠️ IMPORTANT NOTES

### **Data Loss adalah PERMANEN**

```
⚠️  CRITICAL: 
Enkripsi AES-256 tanpa key adalah IMPOSSIBLE to break
Bahkan dengan supercomputer, butuh TRILIUNAN tahun

Jika key hilang dan tidak ada backup:
→ Data HILANG SELAMANYA
→ TIDAK ADA cara untuk recover
```

### **Backup adalah WAJIB**

```
✅ DO:
- Backup keys setiap hari
- Simpan di 3 lokasi berbeda
- Test restore secara berkala
- Encrypt backup dengan password

❌ DON'T:
- Hanya simpan di 1 lokasi
- Lupa backup setelah update
- Simpan di cloud tanpa enkripsi
- Share keys via email/chat
```

---

## 🎯 REKOMENDASI AKHIR

### **Untuk Mencegah Kehilangan:**

1. ✅ **Setup automated backup** (daily)
2. ✅ **Use 3-2-1 backup rule**:
   - 3 copies
   - 2 different media
   - 1 offsite
3. ✅ **Test restore** setiap bulan
4. ✅ **Export keys** setelah setup
5. ✅ **Generate recovery codes**

### **Untuk Recovery:**

1. ✅ **Check backup FIRST** (sebelum panic)
2. ✅ **Use recovery utility** (recover_lost_key.py)
3. ✅ **Backup database** sebelum clear data
4. ✅ **Document** apa yang hilang
5. ✅ **Setup better backup** setelah recovery

---

## 📞 EMERGENCY CHECKLIST

Jika keys hilang:

```
☐ Stay calm
☐ Check backup locations (external drive, cloud, password manager)
☐ Run recover_lost_key.py untuk analysis
☐ Backup current database (sebelum delete data)
☐ Decide: Restore from backup OR start fresh
☐ Document what was lost
☐ Setup better backup system
☐ Test recovery procedure
```

---

**Author**: GitHub Copilot  
**Date**: 5 November 2025  
**Version**: 1.0
