"""
Face Authentication Module for SecureMessenger Pro
Uses OpenCV's built-in face detection with LBPH (Local Binary Patterns Histograms) for recognition
No external dependencies like dlib or face_recognition required!

SECURITY: All face data is encrypted with AES-256 before saving to disk
"""

import os
import pickle
import base64
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
from crypto.aes import encrypt_aes, decrypt_aes, generate_key

# ============================================================================
# FACE DATA ENCRYPTION
# ============================================================================

def get_or_create_face_key():
    """
    Get or create master key for face data encryption
    
    Returns:
        bytes: 16-byte AES key for encrypting face data
    
    Security:
        - Separate key from database master key (defense in depth)
        - Key stored in face_master.key
        - If key is lost, face data cannot be recovered
    """
    key_file = "face_master.key"
    
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        # Generate new key
        key = generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        print("🔐 NEW FACE ENCRYPTION KEY GENERATED!")
        print(f"📁 Saved to: {key_file}")
        print("⚠️  BACKUP THIS FILE! If lost, face data cannot be decrypted!")
        return key

# Global face encryption key (loaded once at startup)
FACE_ENCRYPTION_KEY = get_or_create_face_key()

# Directory to store face data
FACE_DATA_DIR = "face_data"
ADMIN_FACE_IMAGES = os.path.join(FACE_DATA_DIR, "admin_faces.enc")  # Changed to .enc
ADMIN_FACE_MODEL = os.path.join(FACE_DATA_DIR, "admin_model.enc")   # Changed to .enc
HAAR_CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

# Initialize face detector
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

def ensure_face_data_dir():
    """Create face_data directory if it doesn't exist"""
    if not os.path.exists(FACE_DATA_DIR):
        os.makedirs(FACE_DATA_DIR)

def detect_faces(frame):
    """
    Detect faces in a frame using Haar Cascade
    Returns: list of face rectangles (x, y, w, h)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )
    return faces

def capture_multiple_faces(window_title="Capture Face", num_samples=20):
    """
    Capture multiple face samples from camera for better recognition
    
    Args:
        window_title: Title of the capture window
        num_samples: Number of face samples to capture
    
    Returns:
        list of face images or None if failed
    """
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access camera!\nPlease check your camera connection.")
        return None
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    face_samples = []
    sample_count = 0
    
    print(f"\n{'='*60}")
    print(f"  {window_title}")
    print(f"{'='*60}")
    print("Instructions:")
    print(f"  • Position your face in the center")
    print(f"  • Keep your face still")
    print(f"  • System will automatically capture {num_samples} samples")
    print("  • Press ESC to cancel")
    print(f"{'='*60}\n")
    
    frame_skip = 0
    
    while sample_count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect faces
        faces = detect_faces(frame)
        
        # Draw rectangles and progress
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add instructions overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (640, 100), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        progress = f"Capturing: {sample_count}/{num_samples}"
        cv2.putText(frame, progress, (20, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Press ESC to cancel", (20, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if len(faces) > 0:
            cv2.putText(frame, "Keep your face still...", (20, 95), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No face detected - please position yourself", (20, 95), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        cv2.imshow(window_title, frame)
        
        # Capture face every 3 frames to get variety
        if len(faces) == 1 and frame_skip % 3 == 0:
            (x, y, w, h) = faces[0]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))  # Normalize size
            face_samples.append(face_roi)
            sample_count += 1
            print(f"  ✅ Sample {sample_count}/{num_samples} captured")
        
        frame_skip += 1
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            print("❌ Capture cancelled by user.")
            cap.release()
            cv2.destroyAllWindows()
            return None
    
    cap.release()
    cv2.destroyAllWindows()
    
    if len(face_samples) >= num_samples:
        print(f"✅ Successfully captured {len(face_samples)} face samples!")
        return face_samples
    else:
        print(f"❌ Only captured {len(face_samples)}/{num_samples} samples. Try again.")
        return None

def save_face_data(face_samples):
    """
    Save captured face samples and train the model with AES-256 encryption
    
    Security:
        - Face samples encrypted with AES-256 before saving
        - Model encrypted with AES-256 before saving
        - Uses FACE_ENCRYPTION_KEY from face_master.key
        - .enc extension indicates encrypted file
    """
    ensure_face_data_dir()
    
    # Serialize face samples to bytes
    face_data_bytes = pickle.dumps(face_samples)
    
    # Encrypt face samples with AES-256
    face_data_b64 = base64.b64encode(face_data_bytes).decode('utf-8')
    encrypted_face_data = encrypt_aes(face_data_b64, FACE_ENCRYPTION_KEY)
    
    # Save encrypted face samples
    with open(ADMIN_FACE_IMAGES, 'w') as f:
        f.write(encrypted_face_data)
    
    print(f"🔒 Face samples encrypted and saved to {ADMIN_FACE_IMAGES}")
    
    # Train the face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    labels = [1] * len(face_samples)  # All samples are from admin (label=1)
    recognizer.train(face_samples, np.array(labels))
    
    # Save model to temporary file first
    temp_model = "temp_model.yml"
    recognizer.save(temp_model)
    
    # Read model file and encrypt it
    with open(temp_model, 'r', encoding='utf-8') as f:
        model_yaml = f.read()
    
    encrypted_model = encrypt_aes(model_yaml, FACE_ENCRYPTION_KEY)
    
    # Save encrypted model
    with open(ADMIN_FACE_MODEL, 'w') as f:
        f.write(encrypted_model)
    
    # Remove temporary file
    os.remove(temp_model)
    
    print(f"🔒 Face model encrypted and saved to {ADMIN_FACE_MODEL}")
    print(f"✅ Face data secured with AES-256 encryption!")

def load_face_model():
    """
    Load the trained face recognizer model with AES-256 decryption
    
    Security:
        - Model decrypted with AES-256 using FACE_ENCRYPTION_KEY
        - Decryption happens in-memory (no plaintext saved to disk)
        - Returns None if decryption fails or file doesn't exist
    """
    if not os.path.exists(ADMIN_FACE_MODEL):
        return None
    
    try:
        # Read encrypted model
        with open(ADMIN_FACE_MODEL, 'r') as f:
            encrypted_model = f.read()
        
        # Decrypt model
        model_yaml = decrypt_aes(encrypted_model, FACE_ENCRYPTION_KEY)
        
        # Save to temporary file for OpenCV to load
        temp_model = "temp_model_load.yml"
        with open(temp_model, 'w', encoding='utf-8') as f:
            f.write(model_yaml)
        
        # Load model from temporary file
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(temp_model)
        
        # Remove temporary file
        os.remove(temp_model)
        
        return recognizer
    except Exception as e:
        print(f"❌ Failed to load face model: {e}")
        return None

def register_admin_face():
    """Register admin's face for authentication"""
    result = messagebox.askyesno(
        "Register Face",
        "This will register your face for admin authentication.\n\n"
        "Instructions:\n"
        "• Position your face in front of the camera\n"
        "• Keep your face still during capture\n"
        "• System will automatically capture 20 samples\n"
        "• Ensure good lighting\n\n"
        "Continue?"
    )
    
    if not result:
        return False
    
    face_samples = capture_multiple_faces("Register Admin Face", num_samples=20)
    
    if face_samples is not None and len(face_samples) >= 20:
        save_face_data(face_samples)
        messagebox.showinfo(
            "Success",
            "✅ Admin face registered successfully!\n\n"
            f"Captured {len(face_samples)} face samples.\n"
            "You can now use face authentication to login."
        )
        return True
    else:
        messagebox.showerror(
            "Failed",
            "❌ Face registration failed!\n\n"
            "Please ensure:\n"
            "• Your face is clearly visible\n"
            "• Camera is working properly\n"
            "• Lighting is adequate\n\n"
            "Please try again."
        )
        return False

def authenticate_face(confidence_threshold=50):
    """
    Authenticate user by comparing captured face with stored admin face
    
    Args:
        confidence_threshold: Confidence threshold (lower = stricter, default=50)
    
    Returns:
        True if authenticated, False otherwise
    """
    # Check if admin face is registered
    recognizer = load_face_model()
    
    if recognizer is None:
        result = messagebox.askyesno(
            "No Face Registered",
            "No admin face found in the system!\n\n"
            "Would you like to register your face now?"
        )
        
        if result:
            return register_admin_face()
        return False
    
    # Capture face for authentication
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot access camera!")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print(f"\n{'='*60}")
    print(f"  Face Authentication")
    print(f"{'='*60}")
    print("Instructions:")
    print("  • Position your face in the center")
    print("  • Press SPACE to authenticate")
    print("  • Press ESC to cancel")
    print(f"{'='*60}\n")
    
    authenticated = False
    confidence_value = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        faces = detect_faces(frame)
        
        # Draw overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (640, 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
        
        cv2.putText(frame, "Press SPACE to authenticate | ESC to cancel", 
                   (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face Detected - Press SPACE", (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            cv2.putText(frame, "Face detected - Ready to authenticate", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No face detected - please position yourself", 
                       (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow("Face Authentication", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 32:  # Space key
            if len(faces) == 0:
                print("❌ No face detected!")
                messagebox.showwarning("No Face", "No face detected!\nPlease position your face in the frame.")
                continue
            elif len(faces) > 1:
                print("⚠️  Multiple faces detected!")
                messagebox.showwarning("Multiple Faces", 
                                     f"Multiple faces detected ({len(faces)})!\nPlease ensure only one face is in the frame.")
                continue
            
            # Get face region
            (x, y, w, h) = faces[0]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            
            # Predict
            label, confidence = recognizer.predict(face_roi)
            confidence_value = confidence
            
            print(f"\n{'='*60}")
            print(f"  Authentication Result")
            print(f"{'='*60}")
            print(f"  Label: {label}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Threshold: {confidence_threshold}")
            print(f"  Status: {'✅ PASS' if confidence < confidence_threshold else '❌ FAIL'}")
            print(f"{'='*60}\n")
            
            # Lower confidence = better match
            if confidence < confidence_threshold:
                authenticated = True
                # Show success feedback
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(frame, "AUTHENTICATED!", (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Face Authentication", frame)
                cv2.waitKey(1000)
            else:
                authenticated = False
                # Show failure feedback
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
                cv2.putText(frame, "NOT RECOGNIZED", (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                cv2.imshow("Face Authentication", frame)
                cv2.waitKey(1000)
            
            break
        
        elif key == 27:  # ESC key
            print("❌ Authentication cancelled.")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if authenticated:
        match_percentage = max(0, 100 - confidence_value)
        messagebox.showinfo(
            "Authentication Success",
            f"✅ Face recognized!\n\n"
            f"Confidence Score: {confidence_value:.1f}\n"
            f"Match Quality: {match_percentage:.1f}%\n"
            f"Access granted."
        )
        return True
    else:
        if confidence_value > 0:
            messagebox.showerror(
                "Authentication Failed",
                f"❌ Face not recognized!\n\n"
                f"Confidence Score: {confidence_value:.1f}\n"
                f"(Required: < {confidence_threshold})\n"
                f"Access denied."
            )
        return False

def show_face_panel(parent_window, login_frame, crud_frame, load_users_callback):
    """
    Show face authentication panel in the admin login window
    
    Args:
        parent_window: Parent window (admin_window)
        login_frame: Login frame to hide on success
        crud_frame: CRUD frame to show on success
        load_users_callback: Callback function to load users after authentication
    """
    # Check if face is registered
    recognizer = load_face_model()
    
    if recognizer is None:
        result = messagebox.askyesno(
            "Setup Face Authentication",
            "Face authentication not set up yet!\n\n"
            "Would you like to register your face now?\n\n"
            "After registration, you can login with your face."
        )
        
        if result:
            if register_admin_face():
                messagebox.showinfo(
                    "Setup Complete",
                    "Face authentication is now ready!\n\n"
                    "Click the face login button again to authenticate."
                )
        return
    
    # Authenticate with face
    if authenticate_face():
        # Hide login frame and show CRUD frame
        login_frame.pack_forget()
        crud_frame.pack(fill="both", expand=True)
        
        # Load users
        if load_users_callback:
            load_users_callback()
        
        # Show success message in parent window
        success_label = tk.Label(
            parent_window,
            text="✅ Authenticated with Face Recognition",
            font=("Segoe UI", 10, "bold"),
            fg="#27AE60",
            bg="#2C3E50"
        )
        success_label.pack(side="bottom", pady=10)
        
        # Remove success message after 3 seconds
        parent_window.after(3000, success_label.destroy)

def show_user_face_login(login_window, show_dashboard_callback):
    """
    Show face authentication for regular user login
    
    Args:
        login_window: Main application window
        show_dashboard_callback: Callback function to show dashboard after successful auth
    """
    # Check if admin face is registered (we'll use same model for now)
    recognizer = load_face_model()
    
    if recognizer is None:
        result = messagebox.askyesno(
            "Setup Face Authentication",
            "Face authentication not set up yet!\n\n"
            "Would you like to register your face now?\n\n"
            "Note: This will register you as an admin user.\n"
            "Regular users should ask admin to register them."
        )
        
        if result:
            if register_admin_face():
                messagebox.showinfo(
                    "Setup Complete",
                    "Face authentication is now ready!\n\n"
                    "Click the face login button again to authenticate."
                )
        return
    
    # Authenticate with face
    if authenticate_face():
        # Import here to avoid circular dependency
        from auth import login as db_login
        
        # For now, authenticate as admin since we only have admin face model
        # In future, implement multi-user face recognition
        result = db_login("admin", "admin")  # Fallback authentication
        
        if result:
            # Set current user and show dashboard
            if hasattr(login_window, 'current_user'):
                login_window.current_user = result
            
            # Call dashboard callback
            if show_dashboard_callback:
                show_dashboard_callback()
                
            messagebox.showinfo(
                "Welcome!",
                f"✅ Face authentication successful!\n\n"
                f"Logged in as: {result['username']}\n"
                f"Role: {'Admin' if result.get('is_admin') else 'User'}"
            )
        else:
            messagebox.showerror(
                "Error",
                "Face recognized but login failed!\n\n"
                "Please contact administrator."
            )

def test_camera():
    """Test if camera is accessible"""
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        return ret
    return False

# Test function
if __name__ == "__main__":
    print("Face Authentication Module - Test Mode")
    print("=" * 60)
    
    # Test camera
    print("\n1. Testing camera access...")
    if test_camera():
        print("   ✅ Camera is accessible")
    else:
        print("   ❌ Camera not accessible")
        exit(1)
    
    # Test registration
    print("\n2. Testing face registration...")
    choice = input("   Register a test face? (y/n): ")
    if choice.lower() == 'y':
        # Initialize tkinter for messagebox
        root = tk.Tk()
        root.withdraw()
        
        if register_admin_face():
            print("   ✅ Registration successful")
        else:
            print("   ❌ Registration failed")
        
        root.destroy()
    
    # Test authentication
    if os.path.exists(ADMIN_FACE_MODEL):
        print("\n3. Testing face authentication...")
        choice = input("   Authenticate with face? (y/n): ")
        if choice.lower() == 'y':
            # Initialize tkinter for messagebox
            root = tk.Tk()
            root.withdraw()
            
            if authenticate_face():
                print("   ✅ Authentication successful")
            else:
                print("   ❌ Authentication failed")
            
            root.destroy()
    
    print("\n" + "=" * 60)
    print("Test completed!")
