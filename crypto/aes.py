from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def generate_key():
    return get_random_bytes(16)

def encrypt_aes(plaintext, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    data = cipher.nonce + tag + ciphertext
    return base64.b64encode(data).decode()

def decrypt_aes(cipher_b64, key):
    data = base64.b64decode(cipher_b64)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()
