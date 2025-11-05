# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
import base64
import os
import json

# app modules
from db import init_db, get_connection
from auth import login, create_user, ensure_admin
from messages import store_message, fetch_messages, fetch_all_messages, delete_message
from stego_utils import encode_message, decode_message
from crypto.vigenere import vigenere_encrypt, vigenere_decrypt
from crypto.aes import generate_key, encrypt_aes, decrypt_aes
from face_auth import authenticate_face, register_admin_face, show_face_panel



# ---------- UI CONSTANTS - Modern Professional Theme ----------
# Background Colors
BG = "#F5F7FA"              # Light gray-blue background
CARD = "#FFFFFF"            # Pure white cards
BORDER = "#E1E8ED"          # Soft border color
SIDEBAR_BG = "#2C3E50"      # Dark blue-gray sidebar
SIDEBAR_ACTIVE = "#34495E"  # Active menu item

# Accent Colors
ACCENT = "#3498DB"          # Primary blue
ACCENT_HOVER = "#2980B9"    # Darker blue on hover
SUCCESS = "#27AE60"         # Green for success
DANGER = "#E74C3C"          # Red for danger
WARNING = "#F39C12"         # Orange for warnings
ADMIN_ACCENT = "#E74C3C"    # Red for admin features

# Text Colors
TEXT_PRIMARY = "#2C3E50"    # Dark blue-gray
TEXT_SECONDARY = "#7F8C8D"  # Medium gray
TEXT_LIGHT = "#ECF0F1"      # Light text for dark backgrounds
TEXT_MUTED = "#95A5A6"      # Muted gray

# Other Colors
HOVER = "#EBF5FB"           # Light blue hover
INPUT_BG = "#FFFFFF"        # White input background
INPUT_FOCUS = "#3498DB"     # Blue border on focus

# Typography - Better hierarchy
FONT_FAMILY = "Segoe UI"
FONT_DISPLAY = (FONT_FAMILY, 24, "bold")    # Extra large headers
FONT_HEADER = (FONT_FAMILY, 18, "bold")     # Page headers
FONT_SUBHEADER = (FONT_FAMILY, 14, "bold")  # Section headers
FONT_MAIN = (FONT_FAMILY, 10)               # Body text
FONT_SMALL = (FONT_FAMILY, 9)               # Small text
FONT_BUTTON = (FONT_FAMILY, 10, "bold")     # Button text

# Spacing System - Consistent padding/margins
SPACE_XS = 5    # Extra small spacing
SPACE_SM = 10   # Small spacing
SPACE_MD = 15   # Medium spacing
SPACE_LG = 20   # Large spacing
SPACE_XL = 30   # Extra large spacing
SPACE_XXL = 40  # Extra extra large spacing

# Component Sizes
UI_PAD = SPACE_LG           # Standard padding (20px)
CARD_PAD = SPACE_XL         # Card padding (30px)
BTN_PAD_X = 25              # Button horizontal padding
BTN_PAD_Y = 10              # Button vertical padding
INPUT_HEIGHT = 12           # Input field height (ipady)
BORDER_WIDTH = 1            # Standard border width
BORDER_RADIUS = 4           # Border radius (for future CSS)

# ---------- ENCRYPTION ALGORITHMS ----------
def caesar_encrypt(text: str, shift: int) -> str:
    """Caesar cipher encryption"""
    result = []
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            shifted = (ord(char) - ascii_offset + shift) % 26
            result.append(chr(shifted + ascii_offset))
        else:
            result.append(char)
    return ''.join(result)

def caesar_decrypt(text: str, shift: int) -> str:
    """Caesar cipher decryption"""
    return caesar_encrypt(text, -shift)

def xor_encrypt(text: str, key: str) -> str:
    """XOR encryption - returns base64 encoded string"""
    key_bytes = key.encode('utf-8')
    text_bytes = text.encode('utf-8')
    encrypted = bytearray()
    
    for i, byte in enumerate(text_bytes):
        encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    return base64.b64encode(bytes(encrypted)).decode('ascii')

def xor_decrypt(encrypted_b64: str, key: str) -> str:
    """XOR decryption - takes base64 encoded string"""
    key_bytes = key.encode('utf-8')
    encrypted = base64.b64decode(encrypted_b64)
    decrypted = bytearray()
    
    for i, byte in enumerate(encrypted):
        decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    
    return bytes(decrypted).decode('utf-8')

def safe_vig_encrypt(text: str, key: str) -> str:
    """Use vigenere to encrypt text"""
    res = vigenere_encrypt(text, key)
    return res if isinstance(res, str) else res.decode("utf-8")

def safe_vig_decrypt(cipher_str: str, key: str) -> str:
    """Decrypt vigenere"""
    res = vigenere_decrypt(cipher_str, key)
    return res if isinstance(res, str) else res.decode("utf-8")

# ---------- MULTI-ALGORITHM ENCRYPTION ----------
def multi_encrypt(plaintext: str, algorithm_order: list, keys: dict) -> str:
    """
    Encrypt with multiple algorithms in specified order
    algorithm_order: list of algorithm names ['vigenere', 'caesar', 'xor']
    keys: dict with keys for each algorithm
    """
    result = plaintext
    
    for algo in algorithm_order:
        if algo == 'vigenere':
            result = safe_vig_encrypt(result, keys['vigenere'])
        elif algo == 'caesar':
            result = caesar_encrypt(result, keys['caesar'])
        elif algo == 'xor':
            result = xor_encrypt(result, keys['xor'])
    
    return result

def multi_decrypt(ciphertext: str, algorithm_order: list, keys: dict) -> str:
    """
    Decrypt with multiple algorithms in reverse order
    """
    result = ciphertext
    
    # Decrypt in reverse order
    for algo in reversed(algorithm_order):
        if algo == 'vigenere':
            result = safe_vig_decrypt(result, keys['vigenere'])
        elif algo == 'caesar':
            result = caesar_decrypt(result, keys['caesar'])
        elif algo == 'xor':
            result = xor_decrypt(result, keys['xor'])
    
    return result

# ---------- Custom Widgets ----------
class ModernButton(tk.Button):
    """Modern button with better spacing and hover effect"""
    def __init__(self, parent, **kwargs):
        bg_color = kwargs.pop('bg_color', ACCENT)
        hover_bg = kwargs.pop('hover_bg', ACCENT_HOVER if bg_color == ACCENT else DANGER)
        
        super().__init__(
            parent,
            bg=bg_color,
            fg="white",
            font=FONT_BUTTON,
            relief="flat",
            cursor="hand2",
            padx=BTN_PAD_X,
            pady=BTN_PAD_Y,
            bd=0,
            **kwargs
        )
        self.default_bg = bg_color
        self.hover_bg = hover_bg
        self.bind("<Enter>", self._on_hover)
        self.bind("<Leave>", self._on_leave)
    
    def _on_hover(self, e):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, e):
        self.config(bg=self.default_bg)


class ModernEntry(tk.Entry):
    """Modern entry field with better spacing and focus effect"""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=FONT_MAIN,
            bg=INPUT_BG,
            fg=TEXT_PRIMARY,
            relief="solid",
            bd=BORDER_WIDTH,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=INPUT_FOCUS,
            insertbackground=TEXT_PRIMARY,
            **kwargs
        )

# ---------- Algorithm Selection Dialog ----------
class AlgorithmOrderDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Encryption Order")
        self.geometry("600x850")
        self.minsize(600, 850)
        self.configure(bg=BG)
        self.resizable(False, False)
        
        self.result = None
        self.available_algos = ['vigenere', 'caesar', 'xor']
        self.selected_order = []
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Header with better spacing
        header_frame = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        header_frame.pack(fill="x", padx=SPACE_XL, pady=SPACE_XL)
        
        tk.Label(
            header_frame,
            text="🔐 Configure Encryption",
            font=FONT_HEADER,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(pady=(SPACE_XL, SPACE_SM))
        
        tk.Label(
            header_frame,
            text="Select algorithms and define encryption order",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        ).pack(pady=(0, SPACE_XS))
        
        # Requirement notice
        tk.Label(
            header_frame,
            text="⚠️ Minimum 2 algorithms required for super encryption",
            font=("Segoe UI", 9, "bold"),
            bg=CARD,
            fg="#E67E22"
        ).pack(pady=(0, SPACE_XL))
        
        # Main content with consistent spacing
        content = tk.Frame(self, bg=BG)
        content.pack(fill="both", expand=False, padx=SPACE_XL, pady=SPACE_SM)
        
        # Available algorithms section
        tk.Label(
            content,
            text="Available Algorithms:",
            font=FONT_SUBHEADER,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(SPACE_MD, SPACE_XS))
        
        algo_frame = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        algo_frame.pack(fill="x", pady=SPACE_SM)
        
        self.algo_vars = {}
        for algo in self.available_algos:
            var = tk.BooleanVar(value=False)
            self.algo_vars[algo] = var
            
            cb_frame = tk.Frame(algo_frame, bg=CARD)
            cb_frame.pack(fill="x", padx=20, pady=10)
            
            cb = tk.Checkbutton(
                cb_frame,
                text=algo.upper(),
                variable=var,
                font=FONT_MAIN,
                bg=CARD,
                fg=TEXT_PRIMARY,
                selectcolor="white",
                activebackground=CARD,
                command=self._update_order_buttons
            )
            cb.pack(side="left")
            
            # Description
            descriptions = {
                'vigenere': "Polyalphabetic substitution cipher",
                'caesar': "Simple shift cipher (requires shift value)",
                'xor': "Bitwise XOR operation"
            }
            tk.Label(
                cb_frame,
                text=descriptions[algo],
                font=("Segoe UI", 9),
                bg=CARD,
                fg=TEXT_SECONDARY
            ).pack(side="left", padx=(10, 0))
        
        # Order selection section with better spacing
        tk.Label(
            content,
            text="Encryption Order:",
            font=FONT_SUBHEADER,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(SPACE_LG, SPACE_XS))
        
        order_frame = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        order_frame.pack(fill="x", pady=SPACE_SM)
        
        self.order_listbox = tk.Listbox(
            order_frame,
            font=FONT_MAIN,
            bg="white",
            fg=TEXT_PRIMARY,
            relief="flat",
            height=3,
            selectmode=tk.SINGLE
        )
        self.order_listbox.pack(fill="x", padx=SPACE_LG, pady=SPACE_LG)
        
        # Order control buttons
        order_btn_frame = tk.Frame(order_frame, bg=CARD)
        order_btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.up_btn = tk.Button(
            order_btn_frame,
            text="↑ Move Up",
            font=FONT_MAIN,
            bg="white",
            fg=TEXT_PRIMARY,
            relief="solid",
            bd=1,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self._move_up,
            state="disabled"
        )
        self.up_btn.pack(side="left", padx=(0, 10))
        
        self.down_btn = tk.Button(
            order_btn_frame,
            text="↓ Move Down",
            font=FONT_MAIN,
            bg="white",
            fg=TEXT_PRIMARY,
            relief="solid",
            bd=1,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self._move_down,
            state="disabled"
        )
        self.down_btn.pack(side="left")
        
        # Selection counter
        self.selection_counter = tk.Label(
            content,
            text="Selected: 0 algorithms (Minimum: 2)",
            font=("Segoe UI", 10, "bold"),
            bg=BG,
            fg="#E74C3C"
        )
        self.selection_counter.pack(anchor="w", pady=(10, 5))
        
        # Info
        tk.Label(
            content,
            text="💡 Tip: Encryption will be applied in the order listed above",
            font=("Segoe UI", 9),
            bg=BG,
            fg=TEXT_SECONDARY,
            wraplength=450,
            justify="left"
        ).pack(anchor="w", pady=(5, 10))
        
        # Buttons - TWO BUTTONS: Cancel and Save Configuration
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(side="bottom", fill="x", padx=40, pady=(10, 20))

        cancel_btn = tk.Button(
            btn_frame,
            text="✖ Cancel",
            font=FONT_MAIN,
            bg="white",
            fg=TEXT_PRIMARY,
            relief="solid",
            bd=1,
            cursor="hand2",
            padx=20,
            pady=12,
            command=self._on_cancel
        )
        cancel_btn.pack(side="left")

        tk.Frame(btn_frame, bg=BG).pack(side="left", expand=True)

        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Configuration",
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT,
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=12,
            command=self._on_ok,
            bd=0
        )
        save_btn.pack(side="right")

        save_btn.bind("<Enter>", lambda e: save_btn.config(bg="#357ABD"))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=ACCENT))

        self.order_listbox.bind('<<ListboxSelect>>', lambda e: self._update_move_buttons())
    
    def _update_order_buttons(self):
        """Update the order listbox based on selected algorithms"""
        # Get currently selected algorithms
        selected = [algo for algo, var in self.algo_vars.items() if var.get()]
        
        # Preserve existing order where possible
        new_order = [algo for algo in self.selected_order if algo in selected]
        
        # Add newly selected algorithms
        for algo in selected:
            if algo not in new_order:
                new_order.append(algo)
        
        self.selected_order = new_order
        
        # Update listbox
        self.order_listbox.delete(0, tk.END)
        for i, algo in enumerate(self.selected_order, 1):
            self.order_listbox.insert(tk.END, f"{i}. {algo.upper()}")
        
        # Update selection counter
        count = len(self.selected_order)
        if count >= 2:
            self.selection_counter.config(
                text=f"✅ Selected: {count} algorithms (Minimum: 2)",
                fg="#27AE60"
            )
        elif count == 1:
            self.selection_counter.config(
                text=f"⚠️ Selected: {count} algorithm (Need 1 more!)",
                fg="#E67E22"
            )
        else:
            self.selection_counter.config(
                text=f"❌ Selected: {count} algorithms (Minimum: 2)",
                fg="#E74C3C"
            )
    
    def _update_move_buttons(self):
        """Enable/disable move buttons based on selection"""
        selection = self.order_listbox.curselection()
        if selection:
            idx = selection[0]
            self.up_btn.config(state="normal" if idx > 0 else "disabled")
            self.down_btn.config(state="normal" if idx < len(self.selected_order) - 1 else "disabled")
        else:
            self.up_btn.config(state="disabled")
            self.down_btn.config(state="disabled")
    
    def _move_up(self):
        """Move selected algorithm up in order"""
        selection = self.order_listbox.curselection()
        if selection and selection[0] > 0:
            idx = selection[0]
            self.selected_order[idx], self.selected_order[idx-1] = self.selected_order[idx-1], self.selected_order[idx]
            self._update_order_buttons()
            self.order_listbox.selection_set(idx - 1)
            self._update_move_buttons()
    
    def _move_down(self):
        """Move selected algorithm down in order"""
        selection = self.order_listbox.curselection()
        if selection and selection[0] < len(self.selected_order) - 1:
            idx = selection[0]
            self.selected_order[idx], self.selected_order[idx+1] = self.selected_order[idx+1], self.selected_order[idx]
            self._update_order_buttons()
            self.order_listbox.selection_set(idx + 1)
            self._update_move_buttons()
    
    def _on_ok(self):
        if not self.selected_order:
            messagebox.showerror("Error", "Please select at least one algorithm")
            return
        
        # Validate: Super encryption requires minimum 2 algorithms
        if len(self.selected_order) < 2:
            messagebox.showerror(
                "Invalid Configuration",
                "❌ Super Encryption requires at least 2 algorithms!\n\n"
                "You have selected: 1 algorithm\n"
                "Required: 2 or more algorithms\n\n"
                "Please select at least one more algorithm to continue."
            )
            return
        
        self.result = self.selected_order
        self.destroy()
    
    def _on_cancel(self):
        self.result = None
        self.destroy()

# ---------- Keys Input Dialog ----------
class KeysInputDialog(tk.Toplevel):
    def __init__(self, parent, algorithm_order):
        super().__init__(parent)
        self.title("Enter Encryption Keys")
        self.geometry("600x750")
        self.configure(bg=BG)
        self.resizable(False, False)
        
        self.algorithm_order = algorithm_order
        self.result = None
        
        self.transient(parent)
        self.grab_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Header
        header_frame = tk.Frame(self, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🔑 Enter Encryption Keys",
            font=FONT_HEADER,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(pady=20)
        
        tk.Label(
            header_frame,
            text="Provide keys for each selected algorithm",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        ).pack(pady=(0, 20))
        
        # Keys form
        form_frame = tk.Frame(self, bg=BG)
        form_frame.pack(fill="x", expand=False, padx=40, pady=20)
        
        self.key_entries = {}
        
        for algo in self.algorithm_order:
            key_frame = tk.Frame(form_frame, bg=BG)
            key_frame.pack(fill="x", pady=15)
            
            label_text = f"{algo.upper()} Key:"
            if algo == 'caesar':
                label_text += " (shift value 1-25)"
            
            tk.Label(
                key_frame,
                text=label_text,
                font=FONT_MAIN,
                bg=BG,
                fg=TEXT_PRIMARY
            ).pack(anchor="w", pady=(0, 5))
            
            if algo == 'caesar':
                entry = tk.Spinbox(
                    key_frame,
                    from_=1,
                    to=25,
                    font=FONT_MAIN,
                    bg="white",
                    fg=TEXT_PRIMARY,
                    relief="solid",
                    bd=1
                )
            else:
                entry = ModernEntry(key_frame, show="●" if algo != 'caesar' else "")
            
            entry.pack(fill="x", ipady=8)
            self.key_entries[algo] = entry
        
        # Info
        tk.Label(
            form_frame,
            text="⚠️ Remember these keys! You'll need them to decrypt.",
            font=("Segoe UI", 9),
            bg=BG,
            fg=ADMIN_ACCENT,
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=20)
        
        # Buttons - TWO SEPARATE BUTTONS
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(side="bottom", fill="x", padx=40, pady=(15, 25))
        
        # Cancel button
        cancel_btn = tk.Button(
            btn_frame,
            text="✖ Cancel",
            font=FONT_MAIN,
            bg="white",
            fg=TEXT_PRIMARY,
            relief="solid",
            bd=1,
            cursor="hand2",
            padx=25,
            pady=12,
            command=self._on_cancel
        )
        cancel_btn.pack(side="left")

        # Spacer
        tk.Frame(btn_frame, bg=BG).pack(side="left", expand=True)

        # OK button
        ok_btn = tk.Button(
            btn_frame,
            text="✓ Confirm Keys",
            font=("Segoe UI", 10, "bold"),
            bg="#27AE60",  # Green for confirmation
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=12,
            command=self._on_ok,
            bd=0
        )
        ok_btn.pack(side="right")

        
        def ok_hover(e):
            ok_btn.config(bg="#229954")
        
        def ok_leave(e):
            ok_btn.config(bg="#27AE60")
        
        ok_btn.bind("<Enter>", ok_hover)
        ok_btn.bind("<Leave>", ok_leave)
        
        # Focus first entry
        if self.key_entries:
            list(self.key_entries.values())[0].focus()
    
    def _on_ok(self):
        keys = {}
        
        for algo, entry in self.key_entries.items():
            value = entry.get().strip()
            
            if not value:
                messagebox.showerror("Error", f"Please enter a key for {algo.upper()}")
                return
            
            if algo == 'caesar':
                try:
                    shift = int(value)
                    if shift < 1 or shift > 25:
                        raise ValueError()
                    keys[algo] = shift
                except ValueError:
                    messagebox.showerror("Error", "Caesar shift must be between 1-25")
                    return
            else:
                if len(value) < 3:
                    messagebox.showerror("Error", f"{algo.upper()} key must be at least 3 characters")
                    return
                keys[algo] = value
        
        self.result = keys
        self.destroy()
    
    def _on_cancel(self):
        self.result = None
        self.destroy()


# ---------- App ----------
class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SecureMessenger Pro")
        self.geometry("1100x700")
        self.configure(bg=BG)
        
        init_db()
        self._ensure_default_admin()
        
        self.current_user = None
        self.current_screen = None
        
        # Store encryption configuration
        self.encryption_config = None
        self.encryption_keys = None
        
        self._setup_style()
        self.show_login()
    
    def _ensure_default_admin(self):
        """Ensure default admin account exists"""
        try:
            from crypto.hashing import hash_password
            
            conn = get_connection()
            c = conn.cursor()
            
            c.execute("SELECT * FROM users WHERE username=?", ("admin",))
            admin_exists = c.fetchone()
            
            if not admin_exists:
                salt, hashed = hash_password("admin")
                c.execute("INSERT INTO users (username, password_hash, salt, is_admin) VALUES (?, ?, ?, ?)",
                         ("admin", hashed, salt, 1))
                conn.commit()
                print("✅ Default admin created (Username: admin, Password: admin)")
            else:
                if admin_exists[4] != 1:
                    c.execute("UPDATE users SET is_admin=1 WHERE username=?", ("admin",))
                    conn.commit()
            
            conn.close()
        except Exception as e:
            print(f"Error ensuring admin: {e}")

    def _setup_style(self):
        """Configure ttk styles"""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.style.configure("TFrame", background=BG)
        self.style.configure("Card.TFrame", background=CARD, relief="flat")
        
        self.style.configure("TLabel", background=BG, foreground=TEXT_PRIMARY, font=FONT_MAIN)
        self.style.configure("Header.TLabel", font=FONT_HEADER, foreground=TEXT_PRIMARY, background=BG)
        self.style.configure("Subheader.TLabel", font=FONT_SUBHEADER, foreground=TEXT_PRIMARY, background=BG)
        
        self.style.configure("Treeview",
            background="white",
            foreground=TEXT_PRIMARY,
            fieldbackground="white",
            font=FONT_MAIN,
            rowheight=30
        )
        self.style.configure("Treeview.Heading",
            background=CARD,
            foreground=TEXT_PRIMARY,
            font=FONT_SUBHEADER,
            relief="flat"
        )

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ---------- LOGIN SCREEN ----------
    def show_login(self):
        self.clear_screen()
        
        # Create main frame first
        main_frame = tk.Frame(self, bg=BG)
        main_frame.pack(fill="both", expand=True)
        
        # Admin button - IMMEDIATELY after creating main_frame
        # Using after_idle to ensure window is fully rendered
        def create_admin_button():
            admin_btn = tk.Button(
                self,  # Directly on root window
                text="Admin",
                font=("Segoe UI", 10, "bold"),
                bg=ADMIN_ACCENT,
                fg="white",
                relief="raised",
                cursor="hand2",
                padx=15,
                pady=8,
                command=self.show_admin_panel,
                bd=2
            )
            # Place at fixed position
            admin_btn.place(relx=1.0, x=-130, y=10, width=120, height=40)
            
            def admin_hover(e):
                admin_btn.config(bg="#C0392B")
            
            def admin_leave(e):
                admin_btn.config(bg=ADMIN_ACCENT)
            
            admin_btn.bind("<Enter>", admin_hover)
            admin_btn.bind("<Leave>", admin_leave)
        
        # Create button after window updates
        self.after(100, create_admin_button)
        
        # Center card with better size
        card = tk.Frame(main_frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=650)
        
        # Header with improved spacing
        header_frame = tk.Frame(card, bg=CARD)
        header_frame.pack(pady=(SPACE_XXL + SPACE_SM, SPACE_MD))
        
        tk.Label(
            header_frame,
            text="🔐",
            font=("Segoe UI", 56),
            bg=CARD,
            fg=ACCENT
        ).pack()
        
        tk.Label(
            header_frame,
            text="SecureMessenger Pro",
            font=FONT_DISPLAY,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(pady=(SPACE_MD, SPACE_XS))
        
        tk.Label(
            header_frame,
            text="Multi-algorithm encryption system",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        ).pack()
        
        # Form with better spacing
        form_frame = tk.Frame(card, bg=CARD)
        form_frame.pack(pady=SPACE_LG, padx=SPACE_XXL + SPACE_LG, fill="x")
        
        tk.Label(
            form_frame, 
            text="Username", 
            font=FONT_MAIN, 
            bg=CARD, 
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, SPACE_XS))
        ent_user = ModernEntry(form_frame, width=40)
        ent_user.pack(fill="x", ipady=INPUT_HEIGHT)
        
        tk.Label(
            form_frame, 
            text="Password", 
            font=FONT_MAIN, 
            bg=CARD, 
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(SPACE_LG, SPACE_XS))
        ent_pass = ModernEntry(form_frame, width=40, show="●")
        ent_pass.pack(fill="x", ipady=INPUT_HEIGHT)
        
        # Buttons with better spacing
        btn_frame = tk.Frame(card, bg=CARD)
        btn_frame.pack(pady=SPACE_XL, padx=SPACE_XXL + SPACE_MD, fill="x")
        
        def do_login():
            username = ent_user.get().strip()
            password = ent_pass.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            result = login(username, password)
            if result:
                self.current_user = result
                self.show_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")
        
        ModernButton(btn_frame, text="Login", command=do_login).pack(fill="x", pady=(0, SPACE_MD))
        
        register_btn = tk.Button(
            btn_frame,
            text="Create Account",
            font=FONT_BUTTON,
            bg="white",
            fg=ACCENT,
            relief="solid",
            bd=1,
            cursor="hand2",
            command=self.show_register
        )
        register_btn.pack(fill="x", ipady=INPUT_HEIGHT)
        
        # Add hover effect for register button
        def register_hover(e):
            register_btn.config(bg=HOVER, fg=ACCENT)
        
        def register_leave(e):
            register_btn.config(bg="white", fg=ACCENT)
        
        register_btn.bind("<Enter>", register_hover)
        register_btn.bind("<Leave>", register_leave)
        
        ent_user.focus()
        ent_pass.bind("<Return>", lambda e: do_login())

    # ---------- HIDDEN ADMIN PANEL ----------
    def show_admin_panel(self):
        """Hidden admin panel with 2-stage view: login then user CRUD"""
        import json
        admin_window = tk.Toplevel(self)
        admin_window.title("Admin Panel")

        # ✅ Ukuran fleksibel + maximize aktif
        admin_window.geometry("900x600")
        admin_window.minsize(700, 500)
        admin_window.resizable(True, True)
        admin_window.configure(bg=BG)
        admin_window.transient(self)

        # ========== HEADER ==========
        header = tk.Frame(admin_window, bg=ADMIN_ACCENT)
        header.pack(fill="x")
        tk.Label(
            header,
            text="🔧 Administrator Panel",
            font=FONT_HEADER,
            bg=ADMIN_ACCENT,
            fg="white"
        ).pack(pady=(15, 0))
        tk.Label(
            header,
            text="User Management System",
            font=FONT_MAIN,
            bg=ADMIN_ACCENT,
            fg="white"
        ).pack(pady=(0, 15))

        # ========== CONTAINER UTAMA ==========
        container = tk.Frame(admin_window, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- FRAME LOGIN ADMIN ---
        login_frame = tk.Frame(container, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        login_frame.pack(fill="both", expand=True)

        tk.Label(
            login_frame,
            text="🔐 Admin Authentication Required",
            font=FONT_SUBHEADER,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(pady=(30, 10))

        tk.Label(login_frame, text="Username:", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack()
        admin_user = ModernEntry(login_frame, width=30)
        admin_user.pack(ipady=8, pady=(0, 10))

        tk.Label(login_frame, text="Password:", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack()
        admin_pass = ModernEntry(login_frame, width=30, show="●")
        admin_pass.pack(ipady=8, pady=(0, 15))

        login_btn = ModernButton(
            login_frame,
            text="Login as Admin",
            bg_color=ADMIN_ACCENT,
            hover_bg="#C0392B",
            command=lambda: authenticate_admin()
        )
        login_btn.pack(pady=(10, 20))

        # Tombol Login with Face (khusus admin)
        face_btn = ModernButton(
            login_frame,
            text="🧠 Login with Face",
            bg_color="#2980B9",
            hover_bg="#1A5276",
            command=lambda: show_face_panel(admin_window, login_frame, crud_frame, load_users)
        )
        face_btn.pack(pady=(0, 20))


        # --- FRAME CRUD USER (AWALNYA TERSEMBUNYI) ---
        crud_frame = tk.Frame(container, bg=CARD, highlightbackground=BORDER, highlightthickness=1)

        # Subheader
        tk.Label(
            crud_frame,
            text="👥 Manage Users",
            font=FONT_SUBHEADER,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 5))

        # Table container (scrollable)
        table_container = tk.Frame(crud_frame, bg=CARD)
        table_container.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        tree = ttk.Treeview(
            table_container,
            columns=("id", "username", "is_admin"),
            show="headings",
            height=6
        )
        tree.heading("id", text="ID")
        tree.heading("username", text="Username")
        tree.heading("is_admin", text="Admin")

        tree.column("id", width=40, anchor="center")
        tree.column("username", width=180)
        tree.column("is_admin", width=80, anchor="center")

        scroll_y = ttk.Scrollbar(table_container, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(table_container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        # CRUD buttons
        btn_frame = tk.Frame(crud_frame, bg=CARD)
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        add_btn = ModernButton(btn_frame, text="➕ Add User", command=lambda: add_user())
        edit_btn = ModernButton(btn_frame, text="✏️ Edit User", state="disabled", command=lambda: edit_user())
        delete_btn = ModernButton(btn_frame, text="🗑️ Delete User", bg_color=ADMIN_ACCENT, hover_bg="#C0392B", state="disabled", command=lambda: delete_user())
        reset_btn = ModernButton(btn_frame, text="🔄 Reset Password", state="disabled", command=lambda: reset_password())

        add_btn.pack(side="left", padx=5)
        edit_btn.pack(side="left", padx=5)
        delete_btn.pack(side="left", padx=5)
        reset_btn.pack(side="left", padx=5)
        
        # Face Recognition Management Section
        face_frame = tk.Frame(crud_frame, bg=CARD)
        face_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        tk.Label(
            face_frame,
            text="🧠 Face Recognition Management",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        face_btn_frame = tk.Frame(face_frame, bg=CARD)
        face_btn_frame.pack(fill="x")
        
        def edit_face_recognition():
            result = messagebox.askyesno(
                "Re-register Face",
                "This will replace your current face authentication data.\n\n"
                "You will need to capture your face again.\n\n"
                "Continue?"
            )
            
            if result:
                if register_admin_face():
                    messagebox.showinfo(
                        "Success",
                        "✅ Face authentication updated successfully!\n\n"
                        "You can now use the new face data to login."
                    )
        
        def delete_face_recognition():
            result = messagebox.askyesno(
                "Delete Face Data",
                "⚠️ WARNING: This will permanently delete your face authentication data!\n\n"
                "You will need to re-register to use face login again.\n\n"
                "Are you sure?"
            )
            
            if result:
                import os
                from face_auth import ADMIN_FACE_MODEL, ADMIN_FACE_IMAGES
                
                deleted = False
                if os.path.exists(ADMIN_FACE_MODEL):
                    os.remove(ADMIN_FACE_MODEL)
                    deleted = True
                
                if os.path.exists(ADMIN_FACE_IMAGES):
                    os.remove(ADMIN_FACE_IMAGES)
                    deleted = True
                
                if deleted:
                    messagebox.showinfo(
                        "Deleted",
                        "✅ Face authentication data has been deleted.\n\n"
                        "Use 'Re-register Face' to set up face login again."
                    )
                else:
                    messagebox.showwarning(
                        "Not Found",
                        "No face authentication data found."
                    )
        
        reregister_btn = ModernButton(
            face_btn_frame,
            text="🔄 Re-register Face",
            bg_color="#27AE60",
            hover_bg="#229954",
            command=edit_face_recognition
        )
        reregister_btn.pack(side="left", padx=(0, 10))
        
        delete_face_btn = ModernButton(
            face_btn_frame,
            text="🗑️ Delete Face Data",
            bg_color="#E74C3C",
            hover_bg="#C0392B",
            command=delete_face_recognition
        )
        delete_face_btn.pack(side="left")

        # ========== FUNGSI-FUNGSI INTERNAL ==========

        def authenticate_admin():
            username = admin_user.get().strip()
            password = admin_pass.get().strip()

            if not username or not password:
                messagebox.showerror("Error", "Please enter credentials")
                return

            result = login(username, password)
            if not result or not result.get('is_admin'):
                messagebox.showerror("Access Denied", "Invalid credentials or insufficient privileges")
                return

            messagebox.showinfo("Success", "Authenticated successfully")
            login_frame.pack_forget()
            crud_frame.pack(fill="both", expand=True)
            load_users()

        def load_users():
            tree.delete(*tree.get_children())
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, is_admin FROM users ORDER BY id")
            rows = cur.fetchall()
            conn.close()

            for r in rows:
                admin_status = "Yes" if r[2] else "No"
                tree.insert("", "end", values=(r[0], r[1], admin_status))

        def add_user():
            username = simpledialog.askstring("Add User", "Enter new username:", parent=admin_window)
            if not username: return
            username = username.strip()
            if not username:
                messagebox.showerror("Error", "Username cannot be empty")
                return

            password = simpledialog.askstring("Add User", f"Enter password for '{username}':", show="●", parent=admin_window)
            if not password: return
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return

            try:
                success = create_user(username, password, is_admin=0)
                if success:
                    messagebox.showinfo("Success", f"User '{username}' added")
                    load_users()
                else:
                    messagebox.showerror("Error", "Username already exists")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def edit_user():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Select a user to edit")
                return
            item = tree.item(sel[0])["values"]
            uid, username = item[0], item[1]
            if username == "admin":
                messagebox.showerror("Error", "Default admin cannot be edited")
                return

            new_username = simpledialog.askstring("Edit User", "Enter new username:", initialvalue=username, parent=admin_window)
            if not new_username: return
            new_password = simpledialog.askstring("Edit User", "Enter new password (leave blank to keep current):", show="●", parent=admin_window)

            conn = get_connection()
            c = conn.cursor()

            # update username
            if new_username != username:
                c.execute("SELECT id FROM users WHERE username=?", (new_username,))
                if c.fetchone():
                    messagebox.showerror("Error", "Username already exists")
                    conn.close()
                    return
                c.execute("UPDATE users SET username=? WHERE id=?", (new_username, uid))

            # update password
            if new_password:
                from crypto.hashing import hash_password
                salt, hashed = hash_password(new_password)
                c.execute("UPDATE users SET password_hash=?, salt=? WHERE id=?", (hashed, salt, uid))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User updated successfully")
            load_users()

        def delete_user():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Select a user to delete")
                return
            item = tree.item(sel[0])["values"]
            uid, username = item[0], item[1]
            if username == "admin":
                messagebox.showerror("Error", "Cannot delete default admin")
                return
            if not messagebox.askyesno("Confirm", f"Delete user '{username}'? This cannot be undone."):
                return
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id=?", (uid,))
            conn.commit()
            conn.close()
            load_users()
            messagebox.showinfo("Success", f"User '{username}' deleted")

        def reset_password():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Select a user to reset password")
                return
            item = tree.item(sel[0])["values"]
            uid, username = item[0], item[1]
            npw = simpledialog.askstring("Reset Password", f"Enter new password for {username}:", show="●")
            if not npw: return
            if len(npw) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            from crypto.hashing import hash_password
            salt, hashed = hash_password(npw)
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET password_hash=?, salt=? WHERE id=?", (hashed, salt, uid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Password reset for '{username}'")

        # aktifkan tombol CRUD hanya saat user dipilih
        def on_select(event):
            sel = tree.selection()
            if not sel:
                edit_btn.config(state="disabled")
                delete_btn.config(state="disabled")
                reset_btn.config(state="disabled")
                return
            item = tree.item(sel[0])["values"]
            username = item[1]
            if username == "admin":
                edit_btn.config(state="disabled")
                delete_btn.config(state="disabled")
                reset_btn.config(state="disabled")
            else:
                edit_btn.config(state="normal")
                delete_btn.config(state="normal")
                reset_btn.config(state="normal")

        tree.bind("<<TreeviewSelect>>", on_select)
        admin_user.focus()
        admin_pass.bind("<Return>", lambda e: authenticate_admin())


    # ---------- REGISTER SCREEN ----------
    def show_register(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self, bg=BG)
        main_frame.pack(fill="both", expand=True)
        
        card = tk.Frame(main_frame, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=600)
        
        header_frame = tk.Frame(card, bg=CARD)
        header_frame.pack(pady=(SPACE_XXL, SPACE_MD))
        
        tk.Label(
            header_frame,
            text="Create Account",
            font=FONT_DISPLAY,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(pady=(SPACE_SM, SPACE_XS))
        
        tk.Label(
            header_frame,
            text="Join SecureMessenger Pro today",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        ).pack()
        
        form_frame = tk.Frame(card, bg=CARD)
        form_frame.pack(pady=SPACE_LG, padx=SPACE_XXL + SPACE_MD, fill="x")
        
        tk.Label(form_frame, text="Username", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, SPACE_XS))
        ent_user = ModernEntry(form_frame, width=40)
        ent_user.pack(fill="x", ipady=INPUT_HEIGHT)
        
        tk.Label(form_frame, text="Password", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(SPACE_LG, SPACE_XS))
        ent_pass = ModernEntry(form_frame, width=40, show="●")
        ent_pass.pack(fill="x", ipady=INPUT_HEIGHT)
        
        tk.Label(form_frame, text="Confirm Password", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(SPACE_LG, SPACE_XS))
        ent_confirm = ModernEntry(form_frame, width=40, show="●")
        ent_confirm.pack(fill="x", ipady=INPUT_HEIGHT)
        
        btn_frame = tk.Frame(card, bg=CARD)
        btn_frame.pack(pady=SPACE_XL, padx=SPACE_XXL + SPACE_MD, fill="x")
        
        def do_register():
            username = ent_user.get().strip()
            password = ent_pass.get().strip()
            confirm = ent_confirm.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            
            success = create_user(username, password, is_admin=0)
            if success:
                messagebox.showinfo("Success", "Account created! Please login.")
                self.show_login()
            else:
                messagebox.showerror("Error", "Username already exists")
        
        ModernButton(btn_frame, text="Create Account", command=do_register).pack(fill="x", pady=(0, SPACE_LG))
        
        link_frame = tk.Frame(btn_frame, bg=CARD)
        link_frame.pack()
        
        tk.Label(
            link_frame, 
            text="Already have an account?", 
            font=FONT_MAIN, 
            bg=CARD, 
            fg=TEXT_SECONDARY
        ).pack(side="left")
        
        login_btn = tk.Label(
            link_frame,
            text="Login",
            font=("Segoe UI", 10, "bold"),
            bg=CARD,
            fg=ACCENT,
            cursor="hand2"
        )
        login_btn.pack(side="left", padx=(SPACE_XS, 0))
        login_btn.bind("<Button-1>", lambda e: self.show_login())
        
        # Add hover effect for login link
        def login_hover(e):
            login_btn.config(fg=ACCENT_HOVER)
        
        def login_leave(e):
            login_btn.config(fg=ACCENT)
        
        login_btn.bind("<Enter>", login_hover)
        login_btn.bind("<Leave>", login_leave)
        
        ent_user.focus()

    # ---------- DASHBOARD ----------
    def show_dashboard(self):
        self.clear_screen()
        
        # Reset encryption config when entering dashboard
        self.encryption_config = None
        self.encryption_keys = None
        
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)
        
        # Modern Sidebar with dark theme
        sidebar = tk.Frame(container, bg=SIDEBAR_BG, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Sidebar header with icon
        sidebar_header = tk.Frame(sidebar, bg=SIDEBAR_BG)
        sidebar_header.pack(fill="x", pady=SPACE_XL, padx=SPACE_XL)
        
        # App icon
        tk.Label(
            sidebar_header,
            text="🔐",
            font=("Segoe UI", 36),
            bg=SIDEBAR_BG,
            fg=TEXT_LIGHT
        ).pack()
        
        tk.Label(
            sidebar_header,
            text="SecureMessenger Pro",
            font=("Segoe UI", 14, "bold"),
            bg=SIDEBAR_BG,
            fg=TEXT_LIGHT
        ).pack(pady=(SPACE_SM, SPACE_XS))
        
        tk.Label(
            sidebar_header,
            text=f"@{self.current_user['username']}",
            font=FONT_MAIN,
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED
        ).pack()
        
        # Separator line
        tk.Frame(sidebar, bg="#34495E", height=1).pack(fill="x", padx=SPACE_LG, pady=SPACE_LG)
        
        # Menu with better spacing and organization
        menu_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
        menu_frame.pack(fill="both", expand=True, pady=SPACE_SM)
        
        # Main Section
        tk.Label(
            menu_frame,
            text="MAIN",
            font=("Segoe UI", 9, "bold"),
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=SPACE_XL, pady=(SPACE_SM, SPACE_XS))
        
        self._create_menu_item(menu_frame, " Dashboard", lambda: self.show_dashboard_content())
        
        # Messaging Section
        tk.Label(
            menu_frame,
            text="MESSAGING",
            font=("Segoe UI", 9, "bold"),
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=SPACE_XL, pady=(SPACE_LG, SPACE_XS))
        
        self._create_menu_item(menu_frame, " Send Message", lambda: self.show_send())
        self._create_menu_item(menu_frame, " Inbox", lambda: self.show_inbox())
        
        # Security Tools Section
        tk.Label(
            menu_frame,
            text="SECURITY TOOLS",
            font=("Segoe UI", 9, "bold"),
            bg=SIDEBAR_BG,
            fg=TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", padx=SPACE_XL, pady=(SPACE_LG, SPACE_XS))
        
        self._create_menu_item(menu_frame, " Image Stego", lambda: self.show_stego())
        self._create_menu_item(menu_frame, " File Encrypt", lambda: self.show_file_encrypt())
        
        # Logout button with modern styling
        logout_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
        logout_frame.pack(side="bottom", fill="x", pady=SPACE_XL, padx=SPACE_XL)
        
        logout_btn = tk.Button(
            logout_frame,
            text="🚪 Logout",
            font=FONT_BUTTON,
            bg=DANGER,
            fg=TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            command=self._do_logout,
            bd=0
        )
        logout_btn.pack(fill="x", ipady=INPUT_HEIGHT)
        
        def logout_hover(e):
            logout_btn.config(bg="#C0392B")
        
        def logout_leave(e):
            logout_btn.config(bg=DANGER)
        
        logout_btn.bind("<Enter>", logout_hover)
        logout_btn.bind("<Leave>", logout_leave)
        
        # Content area
        self.content_area = tk.Frame(container, bg=BG)
        self.content_area.pack(side="left", fill="both", expand=True)
        
        self.show_dashboard_content()

    def _create_menu_item(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 11),
            bg=SIDEBAR_BG,
            fg=TEXT_LIGHT,
            activebackground=SIDEBAR_ACTIVE,
            activeforeground=TEXT_LIGHT,
            relief="flat",
            cursor="hand2",
            anchor="w",
            padx=SPACE_XL,  # Internal padding untuk text
            pady=SPACE_MD,
            bd=0,
            command=command
        )
        btn.pack(fill="x", pady=SPACE_XS, padx=0)  # No horizontal padding - aligned to edges
        
        def on_hover(e):
            btn.config(bg=SIDEBAR_ACTIVE)
        
        def on_leave(e):
            btn.config(bg=SIDEBAR_BG)
        
        btn.bind("<Enter>", on_hover)
        btn.bind("<Leave>", on_leave)

    def show_dashboard_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        content = tk.Frame(self.content_area, bg=BG)
        content.pack(fill="both", expand=True, padx=SPACE_XL + SPACE_SM, pady=SPACE_XL + SPACE_SM)
        
        tk.Label(
            content,
            text="Dashboard",
            font=FONT_DISPLAY,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        # Stats
        stats_frame = tk.Frame(content, bg=BG)
        stats_frame.pack(fill="x", pady=10)
        
        self._create_stat_card(stats_frame, "👤 User", self.current_user['username'])
        
        user_msgs = len(fetch_messages(self.current_user['username']))
        self._create_stat_card(stats_frame, "📥 Messages", str(user_msgs))
        
        # Info
        info_card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        info_card.pack(fill="both", expand=True, pady=20)
        
        info_content = tk.Frame(info_card, bg=CARD)
        info_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            info_content,
            text="Welcome to SecureMessenger Pro",
            font=FONT_SUBHEADER,
            bg=CARD,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 15))
        
        info_text = (
            "Advanced multi-algorithm encryption system:\n\n"
            "🔐 Multiple Encryption Algorithms:\n"
            "  • Vigenère Cipher - Polyalphabetic substitution\n"
            "  • Caesar Cipher - Classic shift encryption\n"
            "  • XOR Encryption - Bitwise operation\n"
            "  • AES-256 - Military-grade encryption\n\n"
            "    Customizable Encryption Order:\n"
            "    Choose your own algorithm combination and order\n\n"
            "🖼️ Steganography - Hide messages in images\n"
            "📁      File Encryption - Protect sensitive documents\n\n"
            "Use the menu to navigate and start securing your messages!"
        )
        
        tk.Label(
            info_content,
            text=info_text,
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY,
            justify="left"
        ).pack(anchor="w")

    def _create_stat_card(self, parent, title, value):
        card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", padx=(0, 15), ipadx=30, ipady=20)
        
        tk.Label(card, text=title, font=FONT_MAIN, bg=CARD, fg=TEXT_SECONDARY).pack()
        tk.Label(card, text=value, font=("Segoe UI", 20, "bold"), bg=CARD, fg=ACCENT).pack(pady=(5, 0))

    # ---------- SEND MESSAGE ----------
    def show_send(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        content = tk.Frame(self.content_area, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            content,
            text="Send Encrypted Message",
            font=FONT_HEADER,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        form_card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        form_card.pack(fill="both", expand=True)
        
        form_content = tk.Frame(form_card, bg=CARD)
        form_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Recipient
        recipient_frame = tk.Frame(form_content, bg=CARD)
        recipient_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(recipient_frame, text="Recipient Username", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, 5))
        ent_to = ModernEntry(recipient_frame)
        ent_to.pack(fill="x", ipady=8, pady=(0, 5))
        
        # Show available users hint
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username != ?", (self.current_user["username"],))
        available_users = [row[0] for row in c.fetchall()]
        conn.close()
        
        if available_users:
            hint_text = f"💡 Available users: {', '.join(available_users)}"
            tk.Label(
                recipient_frame, 
                text=hint_text, 
                font=("Segoe UI", 9), 
                bg=CARD, 
                fg="#7F8C8D"
            ).pack(anchor="w")
        
        # Message
        tk.Label(form_content, text="Message", font=FONT_MAIN, bg=CARD, fg=TEXT_PRIMARY).pack(anchor="w", pady=(0, 5))
        txt_message = ScrolledText(
            form_content,
            width=60,
            height=10,
            bg="white",
            fg=TEXT_PRIMARY,
            font=FONT_MAIN,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT
        )
        txt_message.pack(fill="both", expand=False, pady=(0, 10))
        
        # Configuration status display
        config_status_frame = tk.Frame(form_content, bg=CARD)
        config_status_frame.pack(fill="x", pady=(0, 15))
        
        config_status_label = tk.Label(
            config_status_frame,
            text="⚙️ Configuration: Not configured",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        )
        config_status_label.pack(anchor="w")
        
        def update_config_status():
            if self.encryption_config and self.encryption_keys:
                algo_info = " → ".join([a.upper() for a in self.encryption_config])
                config_status_label.config(
                    text=f"✓ Configuration: {algo_info} → AES-256",
                    fg="#27AE60"
                )
            else:
                config_status_label.config(
                    text="⚙️ Configuration: Not configured",
                    fg=TEXT_SECONDARY
                )
        
        def configure_encryption():
            # Step 1: Select algorithms
            algo_dialog = AlgorithmOrderDialog(self)
            self.wait_window(algo_dialog)
            
            if not algo_dialog.result:
                return
            
            algorithm_order = algo_dialog.result
            
            # Step 2: Enter keys
            keys_dialog = KeysInputDialog(self, algorithm_order)
            self.wait_window(keys_dialog)
            
            if not keys_dialog.result:
                return
            
            keys = keys_dialog.result
            
            # Save configuration
            self.encryption_config = algorithm_order
            self.encryption_keys = keys
            
            # Update status display
            update_config_status()
            
            algo_info = " → ".join([a.upper() for a in algorithm_order])
            messagebox.showinfo(
                "Configuration Saved",
                f"Encryption configured successfully!\n\n"
                f"Algorithm chain:\n{algo_info} → AES-256\n\n"
                f"You can now send encrypted messages."
            )
        
        def do_send():
            to = ent_to.get().strip()
            msg = txt_message.get("1.0", "end").strip()
            
            if not to or not msg:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            # Validate recipient username exists in database
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id, username FROM users WHERE username=?", (to,))
            recipient = c.fetchone()
            conn.close()
            
            if not recipient:
                messagebox.showerror(
                    "User Not Found", 
                    f"Username '{to}' does not exist!\n\n"
                    f"Please check the username and try again."
                )
                return
            
            if not self.encryption_config or not self.encryption_keys:
                messagebox.showerror("Error", "Please configure encryption first")
                return
            
            try:
                # Multi-algorithm encryption
                encrypted = multi_encrypt(msg, self.encryption_config, self.encryption_keys)
                
                # AES encryption
                aes_key = generate_key()
                aes_key_b64 = base64.b64encode(aes_key).decode()
                cipher = encrypt_aes(encrypted, aes_key)
                
                # Create metadata
                metadata = {
                    'algorithms': self.encryption_config,
                    'aes_key': aes_key_b64
                }
                metadata_str = json.dumps(metadata)
                
                # Store: metadata::cipher
                payload = metadata_str + "::" + cipher
                
                store_message(self.current_user["username"], to, payload)
                
                # Show success with algorithm info
                algo_info = " → ".join([a.upper() for a in self.encryption_config])
                messagebox.showinfo(
                    "Success", 
                    f"Message encrypted and sent!\n\n"
                    f"Encryption chain:\n{algo_info} → AES-256\n\n"
                    f"The recipient will need your encryption keys to decrypt."
                )
                
                ent_to.delete(0, "end")
                txt_message.delete("1.0", "end")
            except Exception as e:
                print("Send error:", e)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to send message: {str(e)}")
        
        # Button frame with TWO SEPARATE BUTTONS
        btn_frame = tk.Frame(form_content, bg=CARD)
        btn_frame.pack(anchor="e", fill="x", pady=(15, 0))  # <-- tambahin fill & padding biar muncul

        ModernButton(
            btn_frame,
            text="⚙️ Configure Encryption",
            bg_color="#9B59B6",
            hover_bg="#8E44AD",
            command=configure_encryption
        ).pack(side="left", padx=(0, 10))

        ModernButton(
            btn_frame,
            text="📤 Send Message",
            command=do_send
        ).pack(side="left")


    # ---------- INBOX ----------
    def show_inbox(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        content = tk.Frame(self.content_area, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            content,
            text="Inbox",
            font=FONT_HEADER,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        messages_card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        messages_card.pack(fill="both", expand=True)
        
        tree_frame = tk.Frame(messages_card, bg=CARD)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tree = ttk.Treeview(tree_frame, columns=("id", "from", "to", "time"), show="headings", height=15)
        tree.heading("id", text="ID")
        tree.heading("from", text="From")
        tree.heading("to", text="To")
        tree.heading("time", text="Time")
        
        tree.column("id", width=50)
        tree.column("from", width=150)
        tree.column("to", width=150)
        tree.column("time", width=200)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        rows = fetch_messages(self.current_user['username'])
        for r in rows:
            if len(r) == 5:
                _id, sender, receiver, content, ts = r
            else:
                sender, receiver, content, ts = r
                _id = ""
            tree.insert("", "end", values=(_id, sender, receiver, ts))
        
        btn_frame = tk.Frame(messages_card, bg=CARD)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def read_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showerror("Error", "Please select a message")
                return
            
            item = tree.item(sel[0])["values"]
            msg_id = item[0]
            
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT sender, receiver, content, timestamp FROM messages WHERE id=?", (msg_id,))
            row = c.fetchone()
            conn.close()
            
            if not row:
                messagebox.showerror("Error", "Message not found")
                return
            
            # IMPORTANT: Decrypt database-level encryption first!
            from db_encryption import decrypt_message_content
            sender_enc, receiver_enc, payload_enc, ts = row
            sender, receiver, payload = decrypt_message_content(sender_enc, receiver_enc, payload_enc)
            
            if "::" not in payload:
                messagebox.showerror("Error", "Invalid message format")
                return
            
            try:
                metadata_str, cipher_b64 = payload.split("::", 1)
                metadata = json.loads(metadata_str)
                
                algorithm_order = metadata['algorithms']
                aes_key_b64 = metadata['aes_key']
                
                # Show algorithm info
                algo_info = " → ".join([a.upper() for a in algorithm_order])
                messagebox.showinfo(
                    "Decryption Info",
                    f"This message uses:\n{algo_info} → AES-256\n\n"
                    f"You'll need to enter keys for each algorithm."
                )
                
                # Get keys from user
                keys_dialog = KeysInputDialog(self, algorithm_order)
                self.wait_window(keys_dialog)
                
                if not keys_dialog.result:
                    return
                
                keys = keys_dialog.result
                
                # Decrypt AES
                aes_key_bytes = base64.b64decode(aes_key_b64)
                encrypted_multi = decrypt_aes(cipher_b64, aes_key_bytes)
                
                # Decrypt multi-algorithm
                plain = multi_decrypt(encrypted_multi, algorithm_order, keys)
                
                # Show message
                msg_win = tk.Toplevel(self)
                msg_win.title(f"Message from {sender}")
                msg_win.geometry("600x400")
                msg_win.configure(bg=BG)
                
                frame = tk.Frame(msg_win, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
                frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                tk.Label(
                    frame,
                    text=f"From: {sender}",
                    font=FONT_SUBHEADER,
                    bg=CARD,
                    fg=TEXT_PRIMARY
                ).pack(anchor="w", padx=20, pady=(20, 10))
                
                txt = ScrolledText(frame, width=60, height=15, bg="white", fg=TEXT_PRIMARY, font=FONT_MAIN)
                txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                txt.insert("1.0", plain)
                txt.config(state="disabled")
            except Exception as e:
                print("Read error:", e)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to decrypt message.\nPlease check your keys.\n\nError: {str(e)}")
        
        ModernButton(btn_frame, text="Read Selected", command=read_selected).pack(side="left", padx=(0, 10))
        ModernButton(btn_frame, text="Refresh", command=self.show_inbox).pack(side="left")

    # ---------- IMAGE STEGO ----------
    def show_stego(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        content = tk.Frame(self.content_area, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            content,
            text="Image Steganography",
            font=FONT_HEADER,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        stego_card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        stego_card.pack(fill="both", expand=True)
        
        stego_content = tk.Frame(stego_card, bg=CARD)
        stego_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            stego_content,
            text="Hide encrypted messages inside images",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))
        
        def do_encode():
            src = filedialog.askopenfilename(title="Select source PNG", filetypes=[("PNG", "*.png")])
            if not src:
                return
            
            msg = simpledialog.askstring("Message", "Enter message to hide:")
            if msg is None or not msg.strip():
                return
            
            out = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if not out:
                return
            
            try:
                aes_key = generate_key()
                aes_key_b64 = base64.b64encode(aes_key).decode('ascii')
                cipher = encrypt_aes(msg, aes_key)
                
                payload = aes_key_b64 + "::" + cipher
                encode_message(src, payload, out)
                
                messagebox.showinfo("Success", f"Message encoded to {os.path.basename(out)}")
            except Exception as e:
                print("Stego encode error:", e)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to encode message: {str(e)}")
        
        def do_decode():
            img = filedialog.askopenfilename(title="Select stego image", filetypes=[("Images", "*.png *.bmp")])
            if not img:
                return
            
            try:
                payload = decode_message(img)
                
                if isinstance(payload, bytes):
                    payload = payload.decode('utf-8', errors='ignore')
                
                if payload.endswith('þ'):
                    payload = payload[:-1]
                
                payload = payload.rstrip('\x00').strip()
                
                if not payload or "::" not in payload:
                    messagebox.showerror("Error", "Invalid or empty payload")
                    return
                
                aes_key_b64, cipher = payload.split("::", 1)
                aes_key_bytes = base64.b64decode(aes_key_b64.strip())
                plain = decrypt_aes(cipher.strip(), aes_key_bytes)
                
                # Show message
                msg_win = tk.Toplevel(self)
                msg_win.title("Decoded Message")
                msg_win.geometry("600x400")
                msg_win.configure(bg=BG)
                
                frame = tk.Frame(msg_win, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
                frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                tk.Label(
                    frame,
                    text="Decoded Message",
                    font=FONT_SUBHEADER,
                    bg=CARD,
                    fg=TEXT_PRIMARY
                ).pack(anchor="w", padx=20, pady=(20, 10))
                
                txt = ScrolledText(frame, width=60, height=15, bg="white", fg=TEXT_PRIMARY, font=FONT_MAIN)
                txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                txt.insert("1.0", plain)
                txt.config(state="disabled")
            except Exception as e:
                print("Stego decode error:", e)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to decode/decrypt: {str(e)}")
        
        ModernButton(stego_content, text="Encode Message into PNG", command=do_encode).pack(pady=5)
        ModernButton(stego_content, text="Decode Message from PNG", command=do_decode).pack(pady=5)

    # ---------- FILE ENCRYPT ----------
    def show_file_encrypt(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        content = tk.Frame(self.content_area, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            content,
            text="File Encryption",
            font=FONT_HEADER,
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        file_card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        file_card.pack(fill="both", expand=True)
        
        file_content = tk.Frame(file_card, bg=CARD)
        file_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        tk.Label(
            file_content,
            text="Encrypt any file with AES-256 encryption",
            font=FONT_MAIN,
            bg=CARD,
            fg=TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 20))
        
        def do_encrypt_file():
            f = filedialog.askopenfilename(title="Select file to encrypt")
            if not f:
                return
            
            out = filedialog.asksaveasfilename(defaultextension=".enc", filetypes=[("Encrypted", "*.enc")])
            if not out:
                return
            
            try:
                with open(f, "rb") as fi:
                    raw = fi.read()
                
                raw_b64 = base64.b64encode(raw).decode()
                aes_key = generate_key()
                aes_key_b64 = base64.b64encode(aes_key).decode()
                cipher = encrypt_aes(raw_b64, aes_key)
                
                with open(out, "w", encoding="utf-8") as fo:
                    fo.write(aes_key_b64 + "::" + cipher)
                
                messagebox.showinfo("Success", f"File encrypted to {os.path.basename(out)}")
            except Exception as e:
                print("File encrypt error:", e)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to encrypt file: {str(e)}")
        
        def do_decrypt_file():
            f = filedialog.askopenfilename(title="Select .enc file", filetypes=[("Encrypted", "*.enc")])
            if not f:
                return
            
            out = filedialog.asksaveasfilename(title="Save decrypted file as")
            if not out:
                return
            
            try:
                with open(f, "r", encoding="utf-8") as fi:
                    content = fi.read()
                
                if "::" not in content:
                    messagebox.showerror("Error", "Invalid .enc file format")
                    return
                
                aes_key_b64, cipher = content.split("::", 1)
                aes_key_bytes = base64.b64decode(aes_key_b64)
                raw_b64 = decrypt_aes(cipher, aes_key_bytes)
                raw = base64.b64decode(raw_b64.encode())
                
                with open(out, "wb") as fo:
                    fo.write(raw)
                
                messagebox.showinfo("Success", f"File decrypted to {os.path.basename(out)}")
            except Exception as e:
                print("File decrypt error:", e)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to decrypt file: {str(e)}")
        
        ModernButton(file_content, text="Encrypt File → .enc", command=do_encrypt_file).pack(pady=5)
        ModernButton(file_content, text="Decrypt .enc → File", command=do_decrypt_file).pack(pady=5)

    def _do_logout(self):
        """Logout and return to login screen"""
        self.current_user = None
        self.show_login()

# ---------- RUN ----------
if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()