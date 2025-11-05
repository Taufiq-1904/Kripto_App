# SecureMessenger Pro 🔐

Aplikasi desktop untuk mengirim dan menerima pesan terenkripsi dengan multiple encryption algorithms.

## 📋 Deskripsi

**SecureMessenger Pro** adalah aplikasi messaging yang menggunakan berbagai algoritma kriptografi untuk mengamankan pesan. Aplikasi ini mendukung:
- **Multi-algorithm encryption** (kombinasi bebas algoritma)
- **Image steganography** (sembunyikan pesan dalam gambar)
- **File encryption** (enkripsi file dengan AES-256)
- **User authentication** dengan password hashing

---

## ✨ Fitur Utama

### 1. Multiple Encryption Algorithms
Aplikasi mendukung 4 algoritma enkripsi:

| Algoritma | Deskripsi | Kekuatan |
|-----------|-----------|----------|
| **Caesar Cipher** | Shift cipher klasik | Basic (untuk pembelajaran) |
| **XOR Encryption** | Operasi bitwise XOR | Medium |
| **Vigenère Cipher** | Polyalphabetic substitution | Medium-High |
| **AES-256 GCM** | Military-grade encryption | Very High |

### 2. Custom Encryption Order
User dapat memilih kombinasi dan urutan algoritma sendiri:
```
Contoh: Vigenère → Caesar → XOR → AES-256
```
Enkripsi berlapis ini memberikan keamanan ekstra.

### 3. Image Steganography
Sembunyikan pesan terenkripsi dalam gambar PNG menggunakan teknik **LSB (Least Significant Bit)**:
- Tidak terlihat oleh mata telanjang
- Kapasitas: ~3.7KB per 100x100 pixel

### 4. File Encryption
Enkripsi file apapun dengan AES-256:
- Hasil file `.enc`
- Password-protected
- Mendukung file besar

### 5. User Authentication
- Password hashing dengan **PBKDF2-HMAC-SHA256**
- Salt unik per user
- 100.000 iterasi (anti brute-force)

### 6. Admin Panel
- User management
- Reset password
- Delete user

---

## 🏗️ Struktur Proyek

```
Kripto_App/
│
├── main.py              # Main application (GUI + logic)
├── auth.py              # Authentication module
├── db.py                # Database operations
├── messages.py          # Message CRUD operations
├── stego_utils.py       # Steganography functions
│
├── crypto/
│   ├── __init__.py
│   ├── aes.py           # AES-256 encryption
│   ├── hashing.py       # Password hashing (PBKDF2)
│   └── vigenere.py      # Vigenère cipher
│
├── secure_messenger.db  # SQLite database (auto-created)
└── README.md            # Dokumentasi ini
```

---

## 🚀 Cara Menjalankan

### Prerequisites
```bash
pip install pillow pycryptodome
```

### Run Application
```bash
python main.py
```

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin`

---

## 📖 Cara Menggunakan

### 1. Register & Login
1. Buka aplikasi
2. Klik "Create Account" untuk registrasi
3. Login dengan username dan password

### 2. Send Encrypted Message
1. Pilih menu "✉️ Send Message"
2. Masukkan username penerima dan pesan
3. Klik "Configure & Send"
4. **Pilih algoritma** (checklist yang diinginkan)
5. **Atur urutan** dengan tombol up/down
6. Klik "Next: Enter Keys"
7. **Input kunci** untuk setiap algoritma
8. Klik "Encrypt & Send Message Now"

### 3. Read Encrypted Message
1. Pilih menu "📥 Inbox"
2. Pilih pesan yang ingin dibaca
3. Klik "Read Selected"
4. **Masukkan kunci** yang sama dengan saat enkripsi
5. Pesan akan didekripsi dan ditampilkan

### 4. Image Steganography
**Encode (Sembunyikan Pesan):**
1. Pilih menu "🖼️ Image Stego"
2. Klik "Encode Message into PNG"
3. Pilih gambar PNG sumber
4. Ketik pesan rahasia
5. Simpan gambar hasil

**Decode (Ekstrak Pesan):**
1. Klik "Decode Message from PNG"
2. Pilih gambar steganografi
3. Pesan akan muncul otomatis

### 5. File Encryption
**Encrypt File:**
1. Pilih menu "📁 File Encrypt"
2. Klik "Encrypt File → .enc"
3. Pilih file yang akan dienkripsi
4. Simpan sebagai `.enc`

**Decrypt File:**
1. Klik "Decrypt .enc → File"
2. Pilih file `.enc`
3. Simpan file hasil dekripsi

### 6. Admin Panel (Hidden)
1. Klik tombol "⚙️ Admin" di pojok kanan atas (login screen)
2. Login dengan akun admin
3. Manage users (delete/reset password)

---

## 🔒 Keamanan

### Password Storage
- **TIDAK** menyimpan password plaintext
- Hashing: PBKDF2-HMAC-SHA256
- Salt: 16 bytes random per user
- Iterasi: 100.000 (slow down brute-force)

### Message Encryption
1. **Multi-algorithm encryption** (user-defined order)
2. **AES-256 GCM** sebagai layer terakhir
3. **Metadata** tersimpan untuk dekripsi:
   ```json
   {
     "algorithms": ["vigenere", "caesar", "xor"],
     "aes_key": "base64_encoded_key"
   }
   ```

### Steganography
- LSB encoding (minimal visual change)
- AES-256 encryption sebelum embedding
- EOF marker (0xFFFE) untuk menandai akhir pesan

---

## 🧩 Penjelasan Algoritma

### Caesar Cipher
```python
# Shift setiap huruf sebanyak N posisi
plaintext:  HELLO
shift: 3
ciphertext: KHOOR
```

### XOR Encryption
```python
# XOR setiap byte dengan kunci
plaintext:  01001000 (H)
key:        01001011 (K)
ciphertext: 00000011 (XOR result)
```

### Vigenère Cipher
```python
# Polyalphabetic substitution
plaintext:  HELLO
key:        KEY (repeated: KEYKE)
ciphertext: RIJVS
```

### AES-256 GCM
- Block cipher (128-bit blocks)
- GCM mode (authenticated encryption)
- Nonce unik per enkripsi
- Tag untuk verifikasi integritas

---

## 📊 Database Schema

### Table: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);
```

### Table: messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    content TEXT NOT NULL,  -- Format: metadata::ciphertext
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 UI/UX

### Design Theme
- **Minimalist White** theme
- Clean and modern interface
- Responsive hover effects
- Card-based layout

### Color Palette
```python
BG = "#FFFFFF"              # Background putih
CARD = "#F8F9FA"            # Card abu-abu muda
ACCENT = "#4A90E2"          # Biru aksen
ADMIN_ACCENT = "#E74C3C"    # Merah untuk admin
```

---

## 🛠️ Dependencies

```
tkinter          # GUI framework (built-in Python)
Pillow           # Image processing untuk steganography
pycryptodome     # AES encryption
sqlite3          # Database (built-in Python)
```

Install:
```bash
pip install pillow pycryptodome
```

---

## 📝 Catatan Penting

### Keamanan Kunci
- **SIMPAN KUNCI DENGAN AMAN!**
- Tanpa kunci yang benar, pesan tidak bisa didekripsi
- Aplikasi tidak menyimpan kunci enkripsi user
- Share kunci secara aman dengan penerima (out-of-band)

### Limitasi
- Image steganography hanya untuk PNG/BMP
- Kapasitas pesan tergantung ukuran gambar
- File encryption tidak memproteksi metadata file

### Best Practices
1. Gunakan kombinasi multiple algorithms untuk keamanan maksimal
2. Gunakan kunci yang kuat (panjang dan random)
3. Jangan gunakan kunci yang sama berulang kali
4. Backup database secara berkala

---

## 🐛 Troubleshooting

### "Image too small to hide message"
**Solusi:** Gunakan gambar yang lebih besar atau kurangi panjang pesan.

### "Failed to decrypt message"
**Solusi:** 
- Pastikan kunci yang dimasukkan benar
- Pastikan urutan algoritma sama dengan saat enkripsi
- Cek case-sensitive untuk kunci

### "Username already exists"
**Solusi:** Pilih username yang berbeda atau login dengan akun yang ada.

---

## 👨‍💻 Author

**Taufiq**
- Repository: [Kripto_App](https://github.com/Taufiq-1904/Kripto_App)
- Course: Kriptografi
- Year: 2025

---

## 📜 License

Proyek ini dibuat untuk tujuan pembelajaran dalam mata kuliah Kriptografi.

---

## 🎓 Penjelasan Konsep Kriptografi

### Symmetric vs Asymmetric Encryption
Aplikasi ini menggunakan **symmetric encryption** (kunci yang sama untuk enkripsi dan dekripsi).

### Layered Security (Defense in Depth)
Menggunakan multiple algorithms memberikan keamanan berlapis. Jika satu algoritma dipecahkan, masih ada lapisan lain.

### Steganography vs Cryptography
- **Cryptography**: Mengubah pesan jadi tidak terbaca
- **Steganography**: Menyembunyikan keberadaan pesan
- Kombinasi keduanya: **Encrypted message hidden in image**

---

## 🔮 Future Enhancements

Ide untuk pengembangan lebih lanjut:
- [ ] RSA encryption (asymmetric)
- [ ] Diffie-Hellman key exchange
- [ ] End-to-end encryption
- [ ] Cloud storage integration
- [ ] Mobile app version
- [ ] Voice message encryption
- [ ] Group messaging
- [ ] 2FA (Two-Factor Authentication)

---

**Selamat menggunakan SecureMessenger Pro! 🚀🔒**
