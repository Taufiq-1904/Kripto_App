def vigenere_encrypt(text, key):
    result = []
    key = key.upper()
    for i, char in enumerate(text):
        if char.isalpha():
            shift = ord(key[i % len(key)]) - 65
            if char.isupper():
                result.append(chr((ord(char) + shift - 65) % 26 + 65))
            else:
                result.append(chr((ord(char) + shift - 97) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)

def vigenere_decrypt(cipher, key):
    result = []
    key = key.upper()
    for i, char in enumerate(cipher):
        if char.isalpha():
            shift = ord(key[i % len(key)]) - 65
            if char.isupper():
                result.append(chr((ord(char) - shift - 65) % 26 + 65))
            else:
                result.append(chr((ord(char) - shift - 97) % 26 + 97))
        else:
            result.append(char)
    return ''.join(result)
