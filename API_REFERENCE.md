# API Reference - SecureMessenger Pro

Dokumentasi lengkap semua fungsi dalam aplikasi.

---

## 📦 Module: main.py

### Encryption Functions

#### `caesar_encrypt(text: str, shift: int) -> str`
Enkripsi teks dengan Caesar cipher.

**Parameters:**
- `text` (str): Plaintext yang akan dienkripsi
- `shift` (int): Jumlah pergeseran (1-25)

**Returns:**
- `str`: Ciphertext

**Example:**
```python
>>> caesar_encrypt("HELLO", 3)
'KHOOR'
>>> caesar_encrypt("Hello World!", 5)
'Mjqqt Btwqi!'
```

---

#### `caesar_decrypt(text: str, shift: int) -> str`
Dekripsi teks Caesar cipher.

**Parameters:**
- `text` (str): Ciphertext
- `shift` (int): Shift yang sama dengan enkripsi

**Returns:**
- `str`: Plaintext

**Example:**
```python
>>> caesar_decrypt("KHOOR", 3)
'HELLO'
```

---

#### `xor_encrypt(text: str, key: str) -> str`
Enkripsi dengan XOR operation.

**Parameters:**
- `text` (str): Plaintext
- `key` (str): Kunci enkripsi

**Returns:**
- `str`: Base64 encoded ciphertext

**Example:**
```python
>>> xor_encrypt("SECRET", "mykey")
'GhwWBBYB'
```

---

#### `xor_decrypt(encrypted_b64: str, key: str) -> str`
Dekripsi XOR ciphertext.

**Parameters:**
- `encrypted_b64` (str): Base64 encoded ciphertext
- `key` (str): Kunci yang sama

**Returns:**
- `str`: Plaintext

---

#### `safe_vig_encrypt(text: str, key: str) -> str`
Wrapper untuk Vigenère encryption.

**Parameters:**
- `text` (str): Plaintext
- `key` (str): Kunci Vigenère

**Returns:**
- `str`: Ciphertext

---

#### `safe_vig_decrypt(cipher_str: str, key: str) -> str`
Wrapper untuk Vigenère decryption.

**Parameters:**
- `cipher_str` (str): Ciphertext
- `key` (str): Kunci yang sama

**Returns:**
- `str`: Plaintext

---

#### `multi_encrypt(plaintext: str, algorithm_order: list, keys: dict) -> str`
Enkripsi multi-algoritma secara berurutan.

**Parameters:**
- `plaintext` (str): Teks asli
- `algorithm_order` (list): List nama algoritma
- `keys` (dict): Dict berisi kunci untuk setiap algoritma

**Returns:**
- `str`: Ciphertext hasil enkripsi berlapis

**Example:**
```python
>>> order = ['caesar', 'xor']
>>> keys = {'caesar': 3, 'xor': 'secret'}
>>> multi_encrypt("HELLO", order, keys)
'base64_encoded_result...'
```

**Supported Algorithms:**
- `'vigenere'` - Kunci: string
- `'caesar'` - Kunci: integer (1-25)
- `'xor'` - Kunci: string

---

#### `multi_decrypt(ciphertext: str, algorithm_order: list, keys: dict) -> str`
Dekripsi multi-algoritma (urutan terbalik).

**Parameters:**
- `ciphertext` (str): Hasil dari multi_encrypt
- `algorithm_order` (list): Order yang SAMA dengan enkripsi
- `keys` (dict): Kunci yang SAMA dengan enkripsi

**Returns:**
- `str`: Plaintext asli

**Note:**
Dekripsi dilakukan dalam urutan TERBALIK dari enkripsi.

---

### Custom Widget Classes

#### `class ModernButton(tk.Button)`
Button dengan hover effect.

**Constructor:**
```python
ModernButton(parent, text="Click", command=callback, bg_color=ACCENT, hover_bg=None)
```

**Parameters:**
- `parent`: Parent widget
- `text` (str): Text button
- `command`: Callback function
- `bg_color` (str): Warna background (default: ACCENT)
- `hover_bg` (str): Warna saat hover (optional)

---

#### `class ModernEntry(tk.Entry)`
Entry field dengan border styling.

**Constructor:**
```python
ModernEntry(parent, show="", width=None)
```

**Parameters:**
- `parent`: Parent widget
- `show` (str): Character untuk password masking (optional)
- `width` (int): Lebar entry (optional)

---

### Dialog Classes

#### `class AlgorithmOrderDialog(tk.Toplevel)`
Dialog untuk memilih urutan algoritma enkripsi.

**Constructor:**
```python
dialog = AlgorithmOrderDialog(parent)
parent.wait_window(dialog)
result = dialog.result  # List of algorithm names atau None
```

**Attributes:**
- `result` (list | None): Urutan algoritma terpilih

**Example:**
```python
>>> dialog = AlgorithmOrderDialog(root)
>>> root.wait_window(dialog)
>>> print(dialog.result)
['vigenere', 'caesar', 'xor']
```

---

#### `class KeysInputDialog(tk.Toplevel)`
Dialog untuk input kunci enkripsi.

**Constructor:**
```python
dialog = KeysInputDialog(parent, algorithm_order)
parent.wait_window(dialog)
result = dialog.result  # Dict of keys atau None
```

**Parameters:**
- `parent`: Parent window
- `algorithm_order` (list): List algoritma yang dipilih

**Attributes:**
- `result` (dict | None): Dictionary berisi kunci

**Example:**
```python
>>> order = ['caesar', 'xor']
>>> dialog = KeysInputDialog(root, order)
>>> root.wait_window(dialog)
>>> print(dialog.result)
{'caesar': 3, 'xor': 'mykey'}
```

---

### Main Application Class

#### `class CryptoApp(tk.Tk)`
Main application class.

**Constructor:**
```python
app = CryptoApp()
app.mainloop()
```

**Public Methods:**
- `show_login()` - Tampilkan login screen
- `show_register()` - Tampilkan register screen
- `show_dashboard()` - Tampilkan dashboard
- `show_admin_panel()` - Tampilkan admin panel

**Private Methods:**
- `_ensure_default_admin()` - Buat admin default
- `_setup_style()` - Setup ttk styles
- `clear_screen()` - Clear all widgets
- `_do_logout()` - Logout user

---

## 📦 Module: auth.py

#### `create_user(username: str, password: str, is_admin: int = 0) -> bool`
Buat user baru dalam database.

**Parameters:**
- `username` (str): Username unik
- `password` (str): Password plaintext (akan di-hash)
- `is_admin` (int): 0=user biasa, 1=admin (default: 0)

**Returns:**
- `bool`: True jika berhasil, False jika username exists

**Example:**
```python
>>> create_user("john", "password123")
True
>>> create_user("john", "another")  # Username exists
False
```

---

#### `login(username: str, password: str) -> dict | None`
Verifikasi kredensial dan login.

**Parameters:**
- `username` (str): Username
- `password` (str): Password plaintext

**Returns:**
- `dict`: User data jika berhasil
- `None`: Jika gagal

**Return Format:**
```python
{
    "id": 1,
    "username": "john",
    "is_admin": 0
}
```

**Example:**
```python
>>> user = login("admin", "admin")
>>> print(user)
{'id': 1, 'username': 'admin', 'is_admin': 1}
>>> login("admin", "wrong")
None
```

---

#### `ensure_admin() -> None`
Pastikan ada admin default.

**Behavior:**
- Cek apakah ada user dengan is_admin=1
- Jika tidak, buat admin default
- Username: `admin`, Password: `admin123`

**Example:**
```python
>>> ensure_admin()  # Buat admin jika belum ada
```

---

## 📦 Module: db.py

#### `get_connection() -> sqlite3.Connection`
Dapatkan koneksi ke database.

**Returns:**
- `sqlite3.Connection`: Connection object

**Example:**
```python
>>> conn = get_connection()
>>> cursor = conn.cursor()
>>> # ... query operations
>>> conn.close()
```

---

#### `init_db() -> None`
Inisialisasi database dan buat tabel.

**Behavior:**
- Buat tabel `users` jika belum ada
- Buat tabel `messages` jika belum ada

**Tables Created:**
1. **users**: id, username, password_hash, salt, is_admin
2. **messages**: id, sender, receiver, content, timestamp

**Example:**
```python
>>> init_db()  # Safe to call multiple times
```

---

## 📦 Module: messages.py

#### `store_message(sender: str, receiver: str, content: str) -> None`
Simpan pesan ke database.

**Parameters:**
- `sender` (str): Username pengirim
- `receiver` (str): Username penerima
- `content` (str): Pesan terenkripsi (format: metadata::ciphertext)

**Example:**
```python
>>> store_message("alice", "bob", "metadata::encrypted_content")
```

---

#### `fetch_messages(username: str) -> list`
Ambil semua pesan untuk user.

**Parameters:**
- `username` (str): Username yang dicari

**Returns:**
- `list`: List of tuples (id, sender, receiver, content, timestamp)

**Example:**
```python
>>> messages = fetch_messages("alice")
>>> for msg in messages:
...     print(f"{msg[1]} -> {msg[2]}: {msg[4]}")
alice -> bob: 2024-01-01 10:00:00
```

---

#### `fetch_all_messages() -> list`
Ambil SEMUA pesan (untuk admin).

**Returns:**
- `list`: List of tuples (id, sender, receiver, content, timestamp)

---

#### `delete_message(message_id: int) -> None`
Hapus pesan berdasarkan ID.

**Parameters:**
- `message_id` (int): ID pesan

**Warning:**
Penghapusan bersifat permanen!

**Example:**
```python
>>> delete_message(5)  # Delete message with ID 5
```

---

## 📦 Module: stego_utils.py

#### `_to_bin(data) -> str`
Konversi data ke binary string.

**Parameters:**
- `data`: str, bytes, atau int

**Returns:**
- `str`: Binary string (8-bit per character)

**Example:**
```python
>>> _to_bin('H')
'01001000'
>>> _to_bin(72)
'01001000'
```

---

#### `encode_message(image_path: str, secret: str, output_path: str) -> bool`
Sembunyikan pesan dalam gambar.

**Parameters:**
- `image_path` (str): Path gambar sumber (PNG/BMP)
- `secret` (str): Pesan rahasia
- `output_path` (str): Path output

**Returns:**
- `bool`: True jika berhasil

**Raises:**
- `ValueError`: Jika gambar terlalu kecil

**Example:**
```python
>>> encode_message('input.png', 'Secret!', 'output.png')
True
```

**Kapasitas:**
- 100x100 pixel = ~3.7KB text
- 500x500 pixel = ~93KB text

---

#### `decode_message(image_path: str) -> str`
Ekstrak pesan dari gambar steganografi.

**Parameters:**
- `image_path` (str): Path gambar stego

**Returns:**
- `str`: Pesan tersembunyi

**Example:**
```python
>>> message = decode_message('stego.png')
>>> print(message)
'Secret!'
```

---

## 📦 Module: crypto/aes.py

#### `generate_key() -> bytes`
Generate kunci AES random.

**Returns:**
- `bytes`: Kunci 16 bytes

**Example:**
```python
>>> key = generate_key()
>>> len(key)
16
```

---

#### `encrypt_aes(plaintext: str, key: bytes) -> str`
Enkripsi dengan AES-GCM.

**Parameters:**
- `plaintext` (str): Teks asli
- `key` (bytes): Kunci AES 16 bytes

**Returns:**
- `str`: Base64 encoded ciphertext

**Example:**
```python
>>> key = generate_key()
>>> cipher = encrypt_aes("Hello", key)
>>> type(cipher)
<class 'str'>
```

---

#### `decrypt_aes(cipher_b64: str, key: bytes) -> str`
Dekripsi AES-GCM.

**Parameters:**
- `cipher_b64` (str): Base64 ciphertext
- `key` (bytes): Kunci yang sama

**Returns:**
- `str`: Plaintext

**Raises:**
- `ValueError`: Jika tag verification gagal

**Example:**
```python
>>> key = generate_key()
>>> cipher = encrypt_aes("Hello", key)
>>> plain = decrypt_aes(cipher, key)
>>> print(plain)
Hello
```

---

## 📦 Module: crypto/hashing.py

#### `hash_password(password: str) -> tuple[str, str]`
Hash password dengan PBKDF2.

**Parameters:**
- `password` (str): Password plaintext

**Returns:**
- `tuple`: (salt_b64, hash_b64)

**Example:**
```python
>>> salt, hashed = hash_password("mypass")
>>> print(f"Salt: {salt[:16]}...")
Salt: a1b2c3d4e5f6g7h8...
```

---

#### `verify_password(password: str, stored_hash: str, stored_salt: str) -> bool`
Verifikasi password.

**Parameters:**
- `password` (str): Password input
- `stored_hash` (str): Hash tersimpan (base64)
- `stored_salt` (str): Salt tersimpan (base64)

**Returns:**
- `bool`: True jika cocok

**Example:**
```python
>>> salt, hashed = hash_password("correct")
>>> verify_password("correct", hashed, salt)
True
>>> verify_password("wrong", hashed, salt)
False
```

---

## 📦 Module: crypto/vigenere.py

#### `vigenere_encrypt(text: str, key: str) -> str`
Enkripsi dengan Vigenère cipher.

**Parameters:**
- `text` (str): Plaintext
- `key` (str): Kunci (kata/frasa)

**Returns:**
- `str`: Ciphertext

**Example:**
```python
>>> vigenere_encrypt("HELLO", "KEY")
'RIJVS'
>>> vigenere_encrypt("hello world", "secret")
'zincs kcvnr'
```

---

#### `vigenere_decrypt(cipher: str, key: str) -> str`
Dekripsi Vigenère.

**Parameters:**
- `cipher` (str): Ciphertext
- `key` (str): Kunci yang sama

**Returns:**
- `str`: Plaintext

**Example:**
```python
>>> vigenere_decrypt("RIJVS", "KEY")
'HELLO'
```

---

## 🔧 Error Handling

### Common Exceptions:

**ValueError**
- Image terlalu kecil untuk steganography
- AES tag verification failed
- Invalid input format

**sqlite3.IntegrityError**
- Username already exists (UNIQUE constraint)

**FileNotFoundError**
- File tidak ditemukan (image/file encryption)

**UnicodeDecodeError**
- Decode error saat steganography

---

## 💡 Best Practices

### 1. Error Handling
```python
try:
    result = multi_encrypt(text, order, keys)
except Exception as e:
    print(f"Encryption failed: {e}")
```

### 2. Resource Management
```python
conn = get_connection()
try:
    # ... database operations
finally:
    conn.close()
```

### 3. Validation
```python
if len(password) < 4:
    raise ValueError("Password too short")
```

### 4. Security
```python
# Jangan log sensitive data
print(f"User logged in: {username}")  # OK
print(f"Password: {password}")         # JANGAN!
```

---

Dokumentasi API lengkap! 🚀
