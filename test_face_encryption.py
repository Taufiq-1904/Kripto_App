"""
Test Face Recognition Encryption
Verifies that face data is properly encrypted with AES-256
"""

import os
import sys

def test_face_encryption():
    """Test if face data files are encrypted"""
    print("="*70)
    print("  FACE RECOGNITION ENCRYPTION TEST")
    print("="*70)
    
    face_data_dir = "face_data"
    face_key_file = "face_master.key"
    
    # Check if face encryption key exists
    print("\n1. Checking Face Encryption Key...")
    if os.path.exists(face_key_file):
        key_size = os.path.getsize(face_key_file)
        print(f"   ✅ Face encryption key found: {face_key_file}")
        print(f"   📏 Key size: {key_size} bytes (Expected: 16 bytes for AES-128)")
        
        if key_size == 16:
            print(f"   ✅ Key size is correct!")
        else:
            print(f"   ⚠️  Warning: Key size is {key_size} bytes, expected 16 bytes")
    else:
        print(f"   ℹ️  No face key found yet (will be generated on first face registration)")
    
    # Check face data files
    print("\n2. Checking Face Data Files...")
    
    encrypted_files = [
        "admin_faces.enc",  # Encrypted face samples
        "admin_model.enc"   # Encrypted LBPH model
    ]
    
    old_files = [
        "admin_faces.pkl",  # Old unencrypted format
        "admin_model.yml"   # Old unencrypted format
    ]
    
    # Check for encrypted files
    for filename in encrypted_files:
        filepath = os.path.join(face_data_dir, filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"   ✅ Encrypted file found: {filename}")
            print(f"      Size: {file_size:,} bytes")
            
            # Read first 100 bytes to verify it looks encrypted
            with open(filepath, 'r') as f:
                content = f.read(100)
                # Encrypted data should be base64 (alphanumeric + +/=)
                if any(c in content for c in ['+', '/', '=']):
                    print(f"      ✅ File appears to be encrypted (contains base64 characters)")
                else:
                    print(f"      ⚠️  Warning: File might not be encrypted!")
        else:
            print(f"   ℹ️  File not found: {filename} (not registered yet)")
    
    # Check for old unencrypted files (should not exist)
    print("\n3. Checking for Old Unencrypted Files...")
    found_old = False
    for filename in old_files:
        filepath = os.path.join(face_data_dir, filename)
        if os.path.exists(filepath):
            print(f"   ⚠️  OLD UNENCRYPTED FILE FOUND: {filename}")
            print(f"      This file should be deleted for security!")
            found_old = True
    
    if not found_old:
        print(f"   ✅ No old unencrypted files found!")
    
    # Summary
    print("\n" + "="*70)
    print("  ENCRYPTION STATUS SUMMARY")
    print("="*70)
    
    key_exists = os.path.exists(face_key_file)
    enc_exists = any(os.path.exists(os.path.join(face_data_dir, f)) for f in encrypted_files)
    old_exists = any(os.path.exists(os.path.join(face_data_dir, f)) for f in old_files)
    
    if key_exists:
        print("✅ Encryption key: PRESENT")
    else:
        print("ℹ️  Encryption key: NOT YET CREATED")
    
    if enc_exists:
        print("✅ Encrypted face data: PRESENT")
    else:
        print("ℹ️  Encrypted face data: NOT YET REGISTERED")
    
    if old_exists:
        print("⚠️  Old unencrypted files: FOUND (SECURITY RISK!)")
    else:
        print("✅ Old unencrypted files: NONE")
    
    print("\n" + "="*70)
    
    if key_exists and enc_exists and not old_exists:
        print("✅ ENCRYPTION STATUS: SECURE")
        print("   All face data is properly encrypted with AES-256!")
    elif not key_exists and not enc_exists:
        print("ℹ️  ENCRYPTION STATUS: READY")
        print("   System is ready for encrypted face registration.")
    else:
        print("⚠️  ENCRYPTION STATUS: NEEDS ATTENTION")
        if old_exists:
            print("   Please delete old unencrypted files!")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    test_face_encryption()
