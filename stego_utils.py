from PIL import Image

def _to_bin(data):
    """Convert data to binary string"""
    if isinstance(data, str):
        # Encode string to UTF-8 bytes first, then to binary
        return ''.join(format(byte, '08b') for byte in data.encode('utf-8'))
    elif isinstance(data, bytes):
        return ''.join(format(byte, '08b') for byte in data)
    elif isinstance(data, int):
        return format(data, '08b')
    else:
        raise TypeError("Unsupported data type.")

def encode_message(image_path, secret, output_path):
    """Encode a secret message into an image using LSB steganography"""
    img = Image.open(image_path)
    
    # Convert secret to binary with EOF marker
    bin_secret = _to_bin(secret) + '1111111111111110'  # EOF marker (0xFFFE in binary)
    
    data_index = 0
    img_data = list(img.getdata())
    new_data = []

    for pixel in img_data:
        r, g, b = [_to_bin(x) for x in pixel[:3]]
        
        # Modify LSB of each color channel
        if data_index < len(bin_secret):
            r = r[:-1] + bin_secret[data_index]
            data_index += 1
        if data_index < len(bin_secret):
            g = g[:-1] + bin_secret[data_index]
            data_index += 1
        if data_index < len(bin_secret):
            b = b[:-1] + bin_secret[data_index]
            data_index += 1
        
        new_pixel = (int(r, 2), int(g, 2), int(b, 2))
        
        # Preserve alpha channel if present
        if len(pixel) == 4:
            new_pixel += (pixel[3],)
        
        new_data.append(new_pixel)
        
        if data_index >= len(bin_secret):
            # Copy remaining pixels unchanged
            new_data.extend(img_data[len(new_data):])
            break

    if data_index < len(bin_secret):
        raise ValueError(f"Image too small to hide message. Need {len(bin_secret)} bits, image has {len(img_data) * 3} bits available.")

    img.putdata(new_data)
    img.save(output_path)
    return True

def decode_message(image_path):
    """Decode a secret message from an image using LSB steganography"""
    img = Image.open(image_path)
    bin_data = ""
    
    # Extract LSB from each pixel
    for pixel in img.getdata():
        r, g, b = pixel[:3]
        bin_data += _to_bin(r)[-1]
        bin_data += _to_bin(g)[-1]
        bin_data += _to_bin(b)[-1]
    
    # Convert binary to bytes
    all_bytes = [bin_data[i:i+8] for i in range(0, len(bin_data), 8)]
    
    decoded_bytes = bytearray()
    eof_marker = bytes([0xFF, 0xFE])  # EOF marker as bytes
    
    for byte_str in all_bytes:
        if len(byte_str) == 8:
            byte_val = int(byte_str, 2)
            decoded_bytes.append(byte_val)
            
            # Check for EOF marker (last 2 bytes = 0xFF 0xFE)
            if len(decoded_bytes) >= 2 and decoded_bytes[-2:] == eof_marker:
                # Remove EOF marker and decode
                decoded_bytes = decoded_bytes[:-2]
                break
    
    # Decode bytes to UTF-8 string
    try:
        decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
        return decoded_str
    except:
        return decoded_bytes.decode('latin-1', errors='ignore')