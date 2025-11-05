# 🚀 Panduan Instalasi & Menjalankan Aplikasi

## ✅ Instalasi Berhasil!

Semua dependencies sudah terinstall:
- ✓ Pillow (image processing)
- ✓ Pycryptodome (AES encryption)
- ✓ PyInstaller (build executable)

---

## 📦 Build Executable Berhasil!

File executable sudah dibuat di:
```
dist\SecureMessenger_Pro.exe
```

---

## 🎯 Cara Menjalankan Aplikasi

### **Opsi 1: Jalankan Executable (RECOMMENDED)**
Cara termudah - tanpa perlu Python:

1. Buka folder `dist`
2. Double-click: **SecureMessenger_Pro.exe**
3. Aplikasi akan langsung jalan! 🎉

**Atau via Command Line:**
```powershell
cd c:\College\Kriptografi\Kripto_App
.\dist\SecureMessenger_Pro.exe
```

### **Opsi 2: Jalankan dari Source Code**
Jika Anda ingin development/debugging:

```powershell
cd c:\College\Kriptografi\Kripto_App
python main.py
```

---

## 🔄 Rebuild Executable

Jika Anda mengubah source code dan ingin rebuild:

### **Cara 1: Menggunakan Batch File (MUDAH)**
```powershell
.\build.bat
```

### **Cara 2: Manual**
```powershell
python -m PyInstaller build_app.spec --clean
```

---

## 📁 Struktur Folder Setelah Build

```
Kripto_App/
│
├── dist/
│   └── SecureMessenger_Pro.exe    ← EXECUTABLE FILE (RUN THIS!)
│
├── build/                          ← Build cache (bisa dihapus)
│
├── main.py                         ← Source code
├── auth.py
├── db.py
├── messages.py
├── stego_utils.py
├── crypto/
│
├── build_app.spec                  ← PyInstaller config
├── build.bat                       ← Build script
├── requirements.txt                ← Dependencies list
│
└── secure_messenger.db             ← Database (auto-created)
```

---

## 🎁 Distribusi Aplikasi

Jika ingin share aplikasi ke orang lain:

1. **Copy file executable:**
   ```
   dist\SecureMessenger_Pro.exe
   ```

2. **Kirim ke user lain**
   - User TIDAK perlu install Python
   - User TIDAK perlu install dependencies
   - Tinggal double-click EXE dan jalan!

3. **Ukuran file:** ~50-60 MB (standalone, include semua dependencies)

---

## ⚠️ Windows Defender Warning

Jika muncul warning dari Windows Defender saat menjalankan:

1. Klik **"More info"**
2. Klik **"Run anyway"**

Ini normal untuk executable yang baru dibuat (belum ada signature).

---

## 🔧 Troubleshooting

### **Error: "python313.dll not found"**
**Solution:** Pastikan Python sudah terinstall dengan benar

### **Error: "Cannot find module xxx"**
**Solution:** Reinstall dependencies:
```powershell
pip install -r requirements.txt
```

### **Executable tidak jalan**
**Solution:** Rebuild dengan flag --onefile:
```powershell
python -m PyInstaller main.py --onefile --windowed --name SecureMessenger_Pro
```

### **Error saat build**
**Solution:** Clear cache dan rebuild:
```powershell
rmdir /s /q build dist
python -m PyInstaller build_app.spec --clean
```

---

## 📝 Default Login

Saat pertama kali menjalankan aplikasi:

**Admin Account:**
- Username: `admin`
- Password: `admin`

**Buat User Baru:**
- Klik "Create Account" di login screen

---

## 🎮 Quick Start

1. **Jalankan aplikasi:**
   ```
   .\dist\SecureMessenger_Pro.exe
   ```

2. **Login atau Register**

3. **Kirim Encrypted Message:**
   - Pilih menu "Send Message"
   - Masukkan username penerima
   - Tulis pesan
   - Pilih algoritma enkripsi
   - Input keys
   - Klik "Save Keys" untuk validasi
   - Klik "Encrypt & Send"

4. **Baca Message:**
   - Pilih menu "Inbox"
   - Pilih pesan
   - Klik "Read Selected"
   - Input keys yang sama
   - Pesan terdekripsi!

---

## 🌟 Fitur yang Tersedia

✅ Multi-algorithm encryption (Caesar, XOR, Vigenère, AES-256)  
✅ Custom encryption order  
✅ Image steganography  
✅ File encryption  
✅ User authentication  
✅ Admin panel  
✅ Save keys before sending (NEW!)  

---

## 📚 Dokumentasi Lengkap

Baca dokumentasi lengkap di:
- **README.md** - Overview dan tutorial
- **TECHNICAL_DOCS.md** - Detail teknis
- **API_REFERENCE.md** - Dokumentasi fungsi

---

## ✨ Selamat Menggunakan SecureMessenger Pro! 🔒

**Aplikasi sudah siap digunakan!**

Untuk menjalankan:
```powershell
cd c:\College\Kriptografi\Kripto_App
.\dist\SecureMessenger_Pro.exe
```

---

**Last Updated:** November 4, 2025  
**Version:** 1.0.0  
**Status:** ✅ Ready to Use!
