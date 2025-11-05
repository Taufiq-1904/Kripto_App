"""
Steganography Utils - Utilitas Steganografi
============================================

Module ini menyediakan fungsi untuk menyembunyikan pesan rahasia
di dalam gambar menggunakan teknik LSB (Least Significant Bit).

Teknik LSB Steganography:
- Mengubah bit terakhir (LSB) dari setiap pixel RGB
- LSB memiliki dampak visual minimal (tidak terlihat mata)
- Dapat menyembunyikan data dalam jumlah besar

Format:
- Input: Gambar PNG/BMP + pesan rahasia
- Output: Gambar dengan pesan tersembunyi (terlihat sama)
- EOF Marker: 0xFFFE (menandai akhir pesan)

Author: Taufiq
Module: stego_utils.py
"""

from PIL import Image

def _to_bin(data):
    """
    Konversi data ke string binary (8-bit)
    
    Fungsi helper untuk mengubah berbagai tipe data menjadi
    representasi binary string.
    
    Args:
        data: Data yang akan dikonversi (str, bytes, atau int)
    
    Returns:
        str: String binary (contoh: '01001000' untuk 'H')
    
    Raises:
        TypeError: Jika tipe data tidak didukung
    
    Example:
        >>> _to_bin('H')
        '01001000'
        >>> _to_bin(72)
        '01001000'
    """
    if isinstance(data, str):
        # String -> UTF-8 bytes -> binary
        return ''.join(format(byte, '08b') for byte in data.encode('utf-8'))
    elif isinstance(data, bytes):
        # Bytes -> binary
        return ''.join(format(byte, '08b') for byte in data)
    elif isinstance(data, int):
        # Integer -> binary (8-bit)
        return format(data, '08b')
    else:
        raise TypeError("Unsupported data type.")

def encode_message(image_path, secret, output_path):
    """
    Encode (Sembunyikan) pesan rahasia ke dalam gambar
    
    Menggunakan teknik LSB (Least Significant Bit) steganography untuk
    menyembunyikan pesan dalam bit terakhir setiap channel warna (R, G, B).
    
    Args:
        image_path (str): Path gambar sumber (PNG/BMP)
        secret (str): Pesan rahasia yang akan disembunyikan
        output_path (str): Path untuk menyimpan gambar hasil
    
    Returns:
        bool: True jika berhasil
    
    Raises:
        ValueError: Jika gambar terlalu kecil untuk menyimpan pesan
    
    Cara Kerja:
        1. Konversi pesan ke binary
        2. Tambahkan EOF marker (0xFFFE) di akhir
        3. Ubah LSB setiap channel RGB dengan bit pesan
        4. Simpan gambar hasil (secara visual sama dengan aslinya)
    
    Kapasitas:
        - Setiap pixel (RGB) dapat menyimpan 3 bit
        - Gambar 100x100 pixel = 30.000 bit = 3.750 byte ≈ 3.7KB teks
    
    Example:
        >>> encode_message('input.png', 'Hello Secret!', 'output.png')
        True
    """
    img = Image.open(image_path)
    
    # Convert secret to binary with EOF marker
    bin_secret = _to_bin(secret) + '1111111111111110'  # EOF marker (0xFFFE in binary)
    
    data_index = 0
    img_data = list(img.getdata())
    new_data = []

    for pixel in img_data:
        r, g, b = [_to_bin(x) for x in pixel[:3]]
        
        # Modifikasi LSB (bit terakhir) dari setiap channel warna
        if data_index < len(bin_secret):
            r = r[:-1] + bin_secret[data_index]  # Ganti bit terakhir R
            data_index += 1
        if data_index < len(bin_secret):
            g = g[:-1] + bin_secret[data_index]  # Ganti bit terakhir G
            data_index += 1
        if data_index < len(bin_secret):
            b = b[:-1] + bin_secret[data_index]  # Ganti bit terakhir B
            data_index += 1
        
        # Konversi binary kembali ke integer RGB
        new_pixel = (int(r, 2), int(g, 2), int(b, 2))
        
        # Pertahankan alpha channel jika ada (RGBA)
        if len(pixel) == 4:
            new_pixel += (pixel[3],)
        
        new_data.append(new_pixel)
        
        # Jika semua data sudah ditanamkan, copy sisa pixel tanpa diubah
        if data_index >= len(bin_secret):
            new_data.extend(img_data[len(new_data):])
            break

    # Validasi: Cek apakah gambar cukup besar
    if data_index < len(bin_secret):
        raise ValueError(f"Image too small to hide message. Need {len(bin_secret)} bits, image has {len(img_data) * 3} bits available.")

    # Simpan gambar hasil
    img.putdata(new_data)
    img.save(output_path)
    return True

def decode_message(image_path):
    """
    Decode (Ekstrak) pesan rahasia dari gambar steganografi
    
    Mengekstrak pesan yang tersembunyi dalam LSB setiap pixel gambar.
    
    Args:
        image_path (str): Path gambar steganografi (yang berisi pesan)
    
    Returns:
        str: Pesan rahasia yang tersembunyi
    
    Cara Kerja:
        1. Ekstrak LSB dari setiap channel RGB
        2. Gabungkan bit menjadi bytes
        3. Baca sampai menemukan EOF marker (0xFFFE)
        4. Decode bytes ke string UTF-8
    
    Example:
        >>> decode_message('stego.png')
        'Hello Secret!'
    
    Note:
        - Gambar harus mengandung pesan yang di-encode dengan encode_message()
        - Jika tidak ada EOF marker, akan membaca seluruh gambar
        - Error handling untuk karakter non-UTF-8
    """
    img = Image.open(image_path)
    bin_data = ""
    
    # Ekstrak LSB (bit terakhir) dari setiap pixel
    for pixel in img.getdata():
        r, g, b = pixel[:3]
        bin_data += _to_bin(r)[-1]  # Ambil bit terakhir R
        bin_data += _to_bin(g)[-1]  # Ambil bit terakhir G
        bin_data += _to_bin(b)[-1]  # Ambil bit terakhir B
    
    # Konversi binary string ke bytes (setiap 8 bit = 1 byte)
    all_bytes = [bin_data[i:i+8] for i in range(0, len(bin_data), 8)]
    
    decoded_bytes = bytearray()
    eof_marker = bytes([0xFF, 0xFE])  # EOF marker (penanda akhir pesan)
    
    # Baca byte demi byte sampai menemukan EOF marker
    for byte_str in all_bytes:
        if len(byte_str) == 8:
            byte_val = int(byte_str, 2)
            decoded_bytes.append(byte_val)
            
            # Cek apakah sudah sampai EOF marker
            if len(decoded_bytes) >= 2 and decoded_bytes[-2:] == eof_marker:
                # Hapus EOF marker dari hasil
                decoded_bytes = decoded_bytes[:-2]
                break
    
    # Decode bytes ke UTF-8 string
    try:
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        return decoded_str
    except:
        # Fallback ke latin-1 jika UTF-8 gagal
        return decoded_bytes.decode('latin-1', errors='ignore')