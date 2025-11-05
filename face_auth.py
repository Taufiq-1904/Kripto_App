import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel

# Folder penyimpanan dataset wajah admin
FACE_DIR = "assets/faces/admin"
os.makedirs(FACE_DIR, exist_ok=True)

# ----------------------------
# === REGISTER FACE ADMIN ===
# ----------------------------
def register_admin_face():
    """Ambil dan simpan dataset wajah admin."""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Camera Error", "Tidak dapat mengakses kamera.")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    count = 0

    messagebox.showinfo("Register Face", "Mengambil sampel wajah admin...\nTekan 'Q' untuk berhenti lebih awal.")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            cv2.imwrite(f"{FACE_DIR}/admin_{count}.jpg", face_img)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Sample {count}/30", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow("📸 Registering Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 30:
            break

    cam.release()
    cv2.destroyAllWindows()

    if count > 0:
        messagebox.showinfo("Success", f"{count} wajah tersimpan di {FACE_DIR}")
    else:
        messagebox.showwarning("Cancelled", "Perekaman wajah dibatalkan.")

# ----------------------------
# === AUTHENTICATE FACE ===
# ----------------------------
def authenticate_face(username="admin"):
    """Login admin jika wajah cocok dengan dataset LBPH."""
    if not os.path.exists(FACE_DIR) or not os.listdir(FACE_DIR):
        messagebox.showwarning("No Dataset", "Belum ada data wajah. Silakan register terlebih dahulu.")
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, labels = [], []
    label_id = 1
    for file in os.listdir(FACE_DIR):
        path = os.path.join(FACE_DIR, file)
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            faces.append(img)
            labels.append(label_id)

    if not faces:
        messagebox.showerror("Error", "Tidak ada data wajah yang valid.")
        return False

    recognizer.train(faces, np.array(labels))

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Camera Error", "Tidak dapat mengakses kamera.")
        return False

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    messagebox.showinfo("Face Login", "Arahkan wajah ke kamera untuk login.\nTekan 'Q' untuk batal.")

    matches = 0
    attempts = 0
    MAX_ATTEMPTS = 50
    MATCH_THRESHOLD = 3
    CONFIDENCE_THRESHOLD = 120  # lebih toleran

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in detected_faces:
            roi = gray[y:y+h, x:x+w]
            label, confidence = recognizer.predict(roi)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if confidence < CONFIDENCE_THRESHOLD:
                matches += 1
                cv2.putText(frame, f"✅ MATCH ({int(confidence)})", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            else:
                cv2.putText(frame, f"❌ UNKNOWN ({int(confidence)})", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
            attempts += 1

        cv2.imshow("🧠 Face Login", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or attempts >= MAX_ATTEMPTS:
            break

    cam.release()
    cv2.destroyAllWindows()

    if matches >= MATCH_THRESHOLD:
        return True
    else:
        return False

# ----------------------------
# === FACE PANEL (BARU) ===
# ----------------------------
def show_face_panel(parent, login_frame, crud_frame, load_users_func):
    """Popup panel pilihan login/register face untuk admin."""
    win = Toplevel(parent)
    win.title("Face Recognition Options")
    win.geometry("350x220")
    win.configure(bg="#f4f4f4")
    win.resizable(False, False)
    win.transient(parent)

    tk.Label(
        win,
        text="🧠 Face Recognition",
        font=("Segoe UI", 13, "bold"),
        bg="#f4f4f4",
        fg="#2C3E50"
    ).pack(pady=(20, 5))

    tk.Label(
        win,
        text="Pilih aksi untuk admin:",
        font=("Segoe UI", 10),
        bg="#f4f4f4",
        fg="#7F8C8D"
    ).pack(pady=(0, 10))

    def login_now():
        # Cek wajah
        success = authenticate_face("admin")
        if success:
            messagebox.showinfo("Success", "Admin logged in via face recognition.")
            win.destroy()
            login_frame.pack_forget()
            crud_frame.pack(fill="both", expand=True)
            load_users_func()

    def register_now():
        register_admin_face()

    tk.Button(
        win, text="🎭 Login with Face", bg="#27AE60", fg="white",
        font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
        command=login_now
    ).pack(pady=5, ipadx=10, ipady=5)

    tk.Button(
        win, text="📸 Register New Face", bg="#2980B9", fg="white",
        font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
        command=register_now
    ).pack(pady=5, ipadx=10, ipady=5)

    tk.Button(
        win, text="✖ Cancel", bg="white", fg="#2C3E50",
        font=("Segoe UI", 10), relief="solid", bd=1, cursor="hand2",
        command=win.destroy
    ).pack(pady=(15, 5), ipadx=10, ipady=3)
