# CHANGELOG - SecureMessenger Pro

Dokumentasi perubahan dan pengembangan aplikasi.

---

## [1.0.0] - 2025-11-04

### ✨ Added - Fitur Baru
- **Multi-algorithm encryption system**
  - Support Caesar, XOR, Vigenère, dan AES-256
  - Custom encryption order (user-defined)
  - Layered security untuk keamanan maksimal

- **User Authentication**
  - Register dan login system
  - Password hashing dengan PBKDF2-HMAC-SHA256
  - Salt unik per user (16 bytes random)
  - 100.000 iterasi untuk anti brute-force

- **Encrypted Messaging**
  - Send encrypted messages antar user
  - Inbox untuk membaca pesan
  - Metadata untuk menyimpan info enkripsi
  - AES-256 GCM sebagai layer terakhir

- **Image Steganography**
  - Hide messages dalam gambar PNG/BMP
  - LSB (Least Significant Bit) technique
  - EOF marker untuk deteksi akhir pesan
  - AES encryption sebelum embedding

- **File Encryption**
  - Encrypt any file type
  - AES-256 encryption
  - Output format: .enc
  - Base64 encoding untuk compatibility

- **Admin Panel**
  - Hidden admin panel (button di login screen)
  - User management (view, delete, reset password)
  - Admin authentication required
  - Default admin: username=admin, password=admin

- **Modern UI/UX**
  - Clean white minimalist theme
  - Responsive hover effects
  - Card-based layout
  - Sidebar navigation
  - Custom widgets (ModernButton, ModernEntry)
  - Dialog windows untuk input

### 📚 Documentation
- **README.md**: Dokumentasi utama aplikasi
- **TECHNICAL_DOCS.md**: Penjelasan detail teknis setiap modul
- **API_REFERENCE.md**: Dokumentasi lengkap semua fungsi/API
- **CHANGELOG.md**: File ini
- **Inline comments**: Dokumentasi di setiap file dan fungsi

### 🏗️ Structure
- Modular architecture:
  - main.py: GUI dan logic utama
  - auth.py: Authentication
  - db.py: Database operations
  - messages.py: Message CRUD
  - stego_utils.py: Steganography
  - crypto/: Package untuk algoritma kriptografi

### 🔒 Security Features
- No plaintext password storage
- Cryptographically secure random generators
- Authenticated encryption (AES-GCM)
- Salt untuk password hashing
- Tag verification untuk data integrity

### 📊 Database
- SQLite database: secure_messenger.db
- Tables:
  - users: User credentials dan info
  - messages: Encrypted messages
- Auto-initialization on first run

---

## 🔮 Future Roadmap

### Version 1.1.0 (Planned)
- [ ] RSA encryption (asymmetric)
- [ ] Digital signatures
- [ ] Certificate management
- [ ] Export/import keys

### Version 1.2.0 (Planned)
- [ ] Diffie-Hellman key exchange
- [ ] Perfect Forward Secrecy
- [ ] Automated key rotation
- [ ] Key escrow system

### Version 2.0.0 (Future)
- [ ] End-to-end encryption
- [ ] Real-time messaging
- [ ] Group chat support
- [ ] Voice message encryption
- [ ] Video call encryption
- [ ] Cloud backup (encrypted)
- [ ] Mobile app version
- [ ] 2FA (Two-Factor Authentication)
- [ ] Biometric authentication

---

## 📝 Notes

### Known Issues
- Image steganography terbatas pada format PNG/BMP
- File encryption tidak protect file metadata
- Single user per application instance

### Limitations
- SQLite: Optimal untuk < 10.000 messages
- No real-time sync antar devices
- Local storage only

### Dependencies
```
tkinter          (built-in Python)
Pillow >= 9.0.0
pycryptodome >= 3.15.0
sqlite3          (built-in Python)
```

---

## 🎓 Educational Purpose

Aplikasi ini dibuat untuk:
- Pembelajaran kriptografi
- Demonstrasi algoritma enkripsi
- Understanding layered security
- Practice secure coding

**Not for production use without proper security audit!**

---

## 👨‍💻 Contributors

- **Taufiq** - Initial work dan dokumentasi lengkap
- Repository: [Kripto_App](https://github.com/Taufiq-1904/Kripto_App)

---

## 📜 License

Project ini dibuat untuk tujuan pembelajaran dalam mata kuliah Kriptografi.

---

## 🙏 Acknowledgments

- Prof/Dosen Kriptografi untuk guidance
- Python community untuk libraries
- Crypto textbooks untuk algoritma reference
- Open source community

---

**Last Updated:** November 4, 2025
**Version:** 1.0.0
**Status:** ✅ Complete & Documented
