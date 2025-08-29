

import os
import base64
import mimetypes
import smtplib
import secrets
import string
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from email.message import EmailMessage
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from PIL import Image, ImageTk
from user_auth_gui import UserAuthWindow
import threading
from datetime import datetime

# Project email credentials
PROJECT_EMAIL ="your_email"
APP_PASSWORD = "your_password"

class ImageEncryptionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔐 Image Encryption Tool")
        self.root.geometry("1000x800")
        self.root.configure(bg='#1e1e2e')
        self.root.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Current user
        self.current_user = None
        self.current_page = "home"
        
        # Style configuration
        self.setup_styles()
        
        # Show login window first
        self.show_auth_window()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 1000
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        style = ttk.Style()
        
        # Configure styles
        style.theme_use('clam')
        
        # Button styles
        style.configure('Modern.TButton',
                       background='#7c3aed',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        style.map('Modern.TButton',
                 background=[('active', '#8b5cf6'),
                            ('pressed', '#6d28d9')])
        
        style.configure('Success.TButton',
                       background='#10b981',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        style.map('Success.TButton',
                 background=[('active', '#34d399'),
                            ('pressed', '#059669')])
        
        style.configure('Danger.TButton',
                       background='#ef4444',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        style.map('Danger.TButton',
                 background=[('active', '#f87171'),
                            ('pressed', '#dc2626')])
        
        style.configure('Info.TButton',
                       background='#3b82f6',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        style.map('Info.TButton',
                 background=[('active', '#60a5fa'),
                            ('pressed', '#2563eb')])
        
        # Entry styles
        style.configure('Modern.TEntry',
                       fieldbackground='#374151',
                       foreground='white',
                       borderwidth=1,
                       insertcolor='white')
        
        # Label styles
        style.configure('Title.TLabel',
                       background='#1e1e2e',
                       foreground='#a855f7',
                       font=('Helvetica', 28, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#1e1e2e',
                       foreground='#d1d5db',
                       font=('Helvetica', 14))
        
        style.configure('Modern.TLabel',
                       background='#1e1e2e',
                       foreground='#f3f4f6',
                       font=('Helvetica', 11))
        
        style.configure('ProjectTitle.TLabel',
                       background='#1e1e2e',
                       foreground='#10b981',
                       font=('Helvetica', 16, 'bold'))
        
    def show_auth_window(self):
        """Show authentication window"""
        self.root.withdraw()  # Hide main window
        auth_window = UserAuthWindow(self.root, self.on_auth_success)
        
    def on_auth_success(self, user_data):
        """Called when user successfully authenticates"""
        self.current_user = user_data
        self.root.deiconify()  # Show main window
        self.create_main_interface()
        
    def create_main_interface(self):
        """Create the main application interface"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e2e')
        main_frame.pack(fill='both', expand=True)
        
        # Navigation bar
        self.create_navigation(main_frame)
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg='#1e1e2e')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Show home page by default
        self.show_home_page()
        
    def create_navigation(self, parent):
        """Create navigation bar"""
        nav_frame = tk.Frame(parent, bg='#374151', height=80)
        nav_frame.pack(fill='x', padx=0, pady=0)
        nav_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = tk.Frame(nav_frame, bg='#374151')
        left_frame.pack(side='left', fill='y', padx=20, pady=10)
        
        logo_label = ttk.Label(left_frame, text="🔐", 
                              style='Title.TLabel')
        logo_label.pack(side='left')
        
        title_label = ttk.Label(left_frame, text="Image Encryption Tool", 
                               style='Subtitle.TLabel')
        title_label.pack(side='left', padx=(10, 0))
        
        # Center - Navigation buttons
        center_frame = tk.Frame(nav_frame, bg='#374151')
        center_frame.pack(side='left', fill='y', padx=50, pady=10)
        
        nav_buttons = [
            ("🏠 Home", "home"),
            ("🔒 Encrypt", "encrypt"),
            ("🔓 Decrypt", "decrypt"),
            ("📋 Project Info", "project"),
            ("👤 Profile", "profile")
        ]
        
        for text, page in nav_buttons:
            btn = ttk.Button(center_frame, text=text,
                           command=lambda p=page: self.show_page(p),
                           style='Info.TButton')
            btn.pack(side='left', padx=5)
        
        # Right side - User info and logout
        right_frame = tk.Frame(nav_frame, bg='#374151')
        right_frame.pack(side='right', fill='y', padx=20, pady=10)
        
        user_label = ttk.Label(right_frame, 
                              text=f"Welcome, {self.current_user['username']}",
                              style='Modern.TLabel')
        user_label.pack(side='left', padx=(0, 20))
        
        logout_btn = ttk.Button(right_frame, text="🚪 Logout", 
                               command=self.logout, style='Danger.TButton')
        logout_btn.pack(side='right')
        
    def show_page(self, page):
        """Show specific page"""
        self.current_page = page
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if page == "home":
            self.show_home_page()
        elif page == "encrypt":
            self.show_encrypt_page()
        elif page == "decrypt":
            self.show_decrypt_page()
        elif page == "project":
            self.show_project_info_page()
        elif page == "profile":
            self.show_profile_page()
    
    def show_home_page(self):
        """Show home page"""
        # Header
        header_frame = tk.Frame(self.content_frame, bg='#1e1e2e')
        header_frame.pack(fill='x', pady=(20, 40))
        
        title_label = ttk.Label(header_frame, text="🔐 Image Encryption Tool", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Secure your images with advanced encryption",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(10, 0))
        
        # Feature cards
        cards_frame = tk.Frame(self.content_frame, bg='#1e1e2e')
        cards_frame.pack(fill='both', expand=True, pady=20)
        
        # Configure grid
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        
        # Encrypt card
        encrypt_card = self.create_feature_card(cards_frame, 
                                               "🔒 Encrypt Images", 
                                               "Secure your images with\nstrong encryption",
                                               lambda: self.show_page("encrypt"))
        encrypt_card.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Decrypt card
        decrypt_card = self.create_feature_card(cards_frame,
                                               "🔓 Decrypt Images",
                                               "Restore your encrypted\nimages safely",
                                               lambda: self.show_page("decrypt"))
        decrypt_card.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        # Project info card
        project_card = self.create_feature_card(cards_frame,
                                               "📋 Project Information",
                                               "View detailed project\ninformation and team",
                                               lambda: self.show_page("project"))
        project_card.grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
        
    def create_feature_card(self, parent, title, description, command):
        """Create a feature card"""
        card = tk.Frame(parent, bg='#374151', relief='raised', bd=1)
        card.configure(width=250, height=200)
        card.pack_propagate(False)
        
        # Title
        title_label = ttk.Label(card, text=title, 
                               style='ProjectTitle.TLabel')
        title_label.pack(pady=(30, 10))
        
        # Description
        desc_label = ttk.Label(card, text=description, 
                              style='Modern.TLabel')
        desc_label.pack(pady=10)
        
        # Button
        btn = ttk.Button(card, text="Open", command=command,
                        style='Modern.TButton')
        btn.pack(pady=20)
        
        return card
    
    def show_encrypt_page(self):
        """Show encrypt image page"""
        # Header
        header_frame = tk.Frame(self.content_frame, bg='#1e1e2e')
        header_frame.pack(fill='x', pady=(20, 30))
        
        title_label = ttk.Label(header_frame, text="🔒 Encrypt Images", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Main content
        content = tk.Frame(self.content_frame, bg='#1e1e2e')
        content.pack(fill='both', expand=True)
        
        # Left panel - Controls
        left_panel = tk.Frame(content, bg='#374151', width=350)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)
        
        controls_title = ttk.Label(left_panel, text="Encryption Controls", 
                                  style='Subtitle.TLabel')
        controls_title.pack(pady=20)
        
        ttk.Button(left_panel, text="📁 Select Image to Encrypt", 
                  command=self.select_image_to_encrypt,
                  style='Success.TButton').pack(pady=10, padx=20, fill='x')
        
        # Right panel - Preview
        self.create_preview_panel(content)
        
    def show_decrypt_page(self):
        """Show decrypt image page"""
        # Header
        header_frame = tk.Frame(self.content_frame, bg='#1e1e2e')
        header_frame.pack(fill='x', pady=(20, 30))
        
        title_label = ttk.Label(header_frame, text="🔓 Decrypt Images", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Main content
        content = tk.Frame(self.content_frame, bg='#1e1e2e')
        content.pack(fill='both', expand=True)
        
        # Left panel - Controls
        left_panel = tk.Frame(content, bg='#374151', width=350)
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)
        
        controls_title = ttk.Label(left_panel, text="Decryption Controls", 
                                  style='Subtitle.TLabel')
        controls_title.pack(pady=20)
        
        ttk.Button(left_panel, text="📁 Select Encrypted File", 
                  command=self.select_file_to_decrypt,
                  style='Modern.TButton').pack(pady=10, padx=20, fill='x')
        
        # Right panel - Preview
        self.create_preview_panel(content)
    
    def show_project_info_page(self):
        """Show project information page"""
        # Header
        header_frame = tk.Frame(self.content_frame, bg='#1e1e2e')
        header_frame.pack(fill='x', pady=(20, 30))
        
        title_label = ttk.Label(header_frame, text="📋 Project Information", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Scrollable frame
        canvas = tk.Canvas(self.content_frame, bg='#1e1e2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e2e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Project details
        self.create_project_info_content(scrollable_frame)
        
    def create_project_info_content(self, parent):
        """Create project information content"""
        # Project overview
        overview_frame = tk.LabelFrame(parent, text="📋 Project Overview", 
                                      bg='#374151', fg='#10b981', 
                                      font=('Helvetica', 14, 'bold'))
        overview_frame.pack(fill='x', padx=20, pady=10)
        
        project_info = [
            ("Project Name", "Image Encryption"),
            ("Description", "Implementing Secured Encryption Standards for Images which Contain Secured Data"),
            ("Project Start Date", "06-JULY-2025"),
            ("Project End Date", "28-JULY-2025"),
            ("Project Status", "Completed")
        ]
        
        for i, (label, value) in enumerate(project_info):
            row_frame = tk.Frame(overview_frame, bg='#374151')
            row_frame.pack(fill='x', padx=10, pady=5)
            
            label_widget = ttk.Label(row_frame, text=f"{label}:", 
                                   style='Modern.TLabel')
            label_widget.pack(side='left', anchor='w')
            
            value_widget = ttk.Label(row_frame, text=value, 
                                   style='Subtitle.TLabel')
            value_widget.pack(side='right', anchor='e')
        
        # Developer details
        dev_frame = tk.LabelFrame(parent, text="👥 Developer Details", 
                                 bg='#374151', fg='#3b82f6', 
                                 font=('Helvetica', 14, 'bold'))
        dev_frame.pack(fill='x', padx=20, pady=10)
        
        developers = [
            ("Developer1", "ID1", "developer1@gmail.com"),
            ("Developer2", "ID2", "developer2@gmail.com"),
            ("Developer3", "ID3", "developer3@gmail.com"), 
            ("Developer4", "ID4", "developer4@gmail.com")
        ]
        
        # Headers
        header_frame = tk.Frame(dev_frame, bg='#374151')
        header_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(header_frame, text="Name", style='Modern.TLabel').pack(side='left', padx=20)
        ttk.Label(header_frame, text="Employee ID", style='Modern.TLabel').pack(side='left', padx=60)
        ttk.Label(header_frame, text="Email", style='Modern.TLabel').pack(side='right', padx=20)
        
        # Developer rows
        for name, emp_id, email in developers:
            row_frame = tk.Frame(dev_frame, bg='#374151')
            row_frame.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(row_frame, text=name, style='Modern.TLabel').pack(side='left', padx=20)
            ttk.Label(row_frame, text=emp_id, style='Modern.TLabel').pack(side='left', padx=40)
            ttk.Label(row_frame, text=email, style='Modern.TLabel').pack(side='right', padx=20)
        
        # Company details
        company_frame = tk.LabelFrame(parent, text="🏢 Company Details", 
                                     bg='#374151', fg='#a855f7', 
                                     font=('Helvetica', 14, 'bold'))
        company_frame.pack(fill='x', padx=20, pady=10)
        
        company_info = [
            ("Company Name", "campany_name"),
            ("Email", "contact@company_name.com"),
            ("Contact", "+91-**********"),
            ("Address", "company_address"),
            ("Website", "https://campany_name.com/")
        ]
        
        for label, value in company_info:
            row_frame = tk.Frame(company_frame, bg='#374151')
            row_frame.pack(fill='x', padx=10, pady=5)
            
            label_widget = ttk.Label(row_frame, text=f"{label}:", 
                                   style='Modern.TLabel')
            label_widget.pack(side='left', anchor='w')
            
            value_widget = ttk.Label(row_frame, text=value, 
                                   style='Subtitle.TLabel')
            value_widget.pack(side='right', anchor='e')
    
    def show_profile_page(self):
        """Show user profile page"""
        # Header
        header_frame = tk.Frame(self.content_frame, bg='#374151')
        header_frame.pack(fill='x', pady=(20, 30))
        
        title_label = ttk.Label(header_frame, text="👤 User Profile", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Profile content
        profile_frame = tk.LabelFrame(self.content_frame, text="Profile Information", 
                                     bg='#374151', fg='#10b981', 
                                     font=('Helvetica', 14, 'bold'))
        profile_frame.pack(fill='x', padx=50, pady=30)
        
        # Profile picture placeholder
        pic_frame = tk.Frame(profile_frame, bg='#374151')
        pic_frame.pack(pady=20)
        
        pic_label = tk.Label(pic_frame, text="👤", font=('Helvetica', 48), 
                            bg='#374151', fg='#a855f7')
        pic_label.pack()
        
        # User info
        user_info = [
            ("Username", self.current_user['username']),
            ("Email", self.current_user['email']),
            ("Account Type", "Standard User"),
            ("Member Since", datetime.now().strftime("%B %Y"))
        ]
        
        for label, value in user_info:
            row_frame = tk.Frame(profile_frame, bg='#374151')
            row_frame.pack(fill='x', padx=20, pady=10)
            
            label_widget = ttk.Label(row_frame, text=f"{label}:", 
                                   style='Modern.TLabel')
            label_widget.pack(side='left', anchor='w')
            
            value_widget = ttk.Label(row_frame, text=value, 
                                   style='Subtitle.TLabel')
            value_widget.pack(side='right', anchor='e')
        
    def create_preview_panel(self, parent):
        """Create preview panel for images"""
        right_panel = tk.Frame(parent, bg='#374151')
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Preview title
        preview_title = ttk.Label(right_panel, text="Image Preview", 
                                 style='Subtitle.TLabel')
        preview_title.pack(pady=20)
        
        # Image preview area
        self.preview_frame = tk.Frame(right_panel, bg='#1f2937', 
                                     relief='sunken', bd=2)
        self.preview_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Status area
        status_frame = tk.Frame(right_panel, bg='#374151')
        status_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.status_text = tk.Text(status_frame, height=8, bg='#1f2937', 
                                  fg='#f3f4f6', font=('Consolas', 10),
                                  state='disabled', wrap='word')
        
        status_scrollbar = ttk.Scrollbar(status_frame, orient='vertical', 
                                        command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.pack(side='left', fill='both', expand=True)
        status_scrollbar.pack(side='right', fill='y')
        
        self.log_message("🎉 Ready for encryption/decryption!")
        
    def log_message(self, message):
        """Add message to status log"""
        if hasattr(self, 'status_text'):
            self.status_text.config(state='normal')
            self.status_text.insert('end', f"{message}\n")
            self.status_text.see('end')
            self.status_text.config(state='disabled')
            self.root.update()
        
    def show_image_preview(self, image_path):
        """Display image preview"""
        try:
            # Clear previous preview
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
                
            # Load and resize image
            img = Image.open(image_path)
            
            # Calculate size maintaining aspect ratio
            preview_size = (400, 300)
            img.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Create label and display image
            img_label = tk.Label(self.preview_frame, image=photo, bg='#1f2937')
            img_label.image = photo  # Keep a reference
            img_label.pack(expand=True)
            
            # Image info
            info_label = ttk.Label(self.preview_frame, 
                                  text=f"📄 {os.path.basename(image_path)}\n📐 {img.size[0]}x{img.size[1]}",
                                  style='Modern.TLabel')
            info_label.pack(pady=10)
            
        except Exception as e:
            self.log_message(f"❌ Could not preview image: {e}")
            
    def select_image_to_encrypt(self):
        """Select and encrypt an image"""
        file_path = filedialog.askopenfilename(
            title="Select Image File to Encrypt",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        self.log_message(f"📁 Selected file: {os.path.basename(file_path)}")
        self.show_image_preview(file_path)
        
        # Ask if user wants to proceed
        proceed = messagebox.askyesno("Confirm Encryption", 
                                     f"Do you want to proceed with encrypting:\n{os.path.basename(file_path)}?")
        
        if proceed:
            # Show encryption options dialog
            self.show_encryption_dialog(file_path)
        
    def show_encryption_dialog(self, image_path):
        """Show encryption options dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔐 Encryption Options")
        dialog.geometry("400x350")
        dialog.configure(bg='#1e1e2e')
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#1e1e2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Choose Password Option", 
                               style='Subtitle.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Password option variable
        pwd_option = tk.StringVar(value="manual")
        
        # Manual password option
        manual_frame = tk.Frame(main_frame, bg='#374151', relief='raised', bd=1)
        manual_frame.pack(fill='x', pady=(0, 10))
        
        tk.Radiobutton(manual_frame, text="Enter password manually", 
                      variable=pwd_option, value="manual", 
                      bg='#374151', fg='#f3f4f6', 
                      selectcolor='#7c3aed', font=('Helvetica', 11)).pack(pady=10, padx=10, anchor='w')
        
        # Password entry
        self.pwd_frame = tk.Frame(manual_frame, bg='#374151')
        self.pwd_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(self.pwd_frame, text="Password:", style='Modern.TLabel').pack(anchor='w')
        self.password_entry = ttk.Entry(self.pwd_frame, show="*", style='Modern.TEntry')
        self.password_entry.pack(fill='x', pady=(5, 5))
        
        ttk.Label(self.pwd_frame, text="Confirm Password:", style='Modern.TLabel').pack(anchor='w')
        self.confirm_entry = ttk.Entry(self.pwd_frame, show="*", style='Modern.TEntry')
        self.confirm_entry.pack(fill='x', pady=(5, 0))
        
        # Auto generate option
        auto_frame = tk.Frame(main_frame, bg='#374151', relief='raised', bd=1)
        auto_frame.pack(fill='x', pady=(0, 20))
        
        tk.Radiobutton(auto_frame, text="Generate strong random password", 
                      variable=pwd_option, value="auto", 
                      bg='#374151', fg='#f3f4f6', 
                      selectcolor='#7c3aed', font=('Helvetica', 11)).pack(pady=10, padx=10, anchor='w')
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#1e1e2e')
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy,
                  style='Danger.TButton').pack(side='right', padx=(10, 0))
        
        ttk.Button(button_frame, text="🔒 Encrypt", 
                  command=lambda: self.start_encryption(dialog, image_path, pwd_option.get()),
                  style='Success.TButton').pack(side='right')
        
    def start_encryption(self, dialog, image_path, pwd_option):
        """Start the encryption process"""
        password = None
        
        if pwd_option == "manual":
            password = self.password_entry.get()
            confirm = self.confirm_entry.get()
            
            if not password:
                messagebox.showerror("Error", "Please enter a password!")
                return
                
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match!")
                return
        else:
            password = self.generate_random_password()
            messagebox.showinfo("Generated Password", 
                              f"Generated password: {password}\n\nPlease save this password safely!")
        
        dialog.destroy()
        
        # Start encryption in separate thread
        self.log_message("🔄 Starting encryption...")
        threading.Thread(target=self.encrypt_image_thread, 
                        args=(image_path, password), daemon=True).start()
        
    def encrypt_image_thread(self, image_path, password):
        """Encrypt image in separate thread"""
        try:
            self.encrypt_image(image_path, password, self.current_user['email'])
            # Show success dialog
            self.root.after(0, lambda: messagebox.showinfo("Encryption Successful", 
                                                          "Image encrypted successfully!\nEncrypted file and password sent to your email."))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Encryption failed: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Encryption Failed", 
                                                           f"Encryption failed: {str(e)}"))
            
    def select_file_to_decrypt(self):
        """Select and decrypt a file"""
        file_path = filedialog.askopenfilename(
            title="Select Encrypted File to Decrypt",
            filetypes=[
                ("Encrypted files", "*.encrypted"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        self.log_message(f"📁 Selected encrypted file: {os.path.basename(file_path)}")
        
        # Show password input dialog
        self.show_decrypt_dialog(file_path)
        
    def show_decrypt_dialog(self, encrypted_path):
        """Show decryption password dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔓 Enter Decryption Password")
        dialog.geometry("400x200")
        dialog.configure(bg='#1e1e2e')
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog, bg='#1e1e2e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enter Password to Decrypt", 
                               style='Subtitle.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Password entry
        ttk.Label(main_frame, text="Password:", style='Modern.TLabel').pack(anchor='w')
        password_entry = ttk.Entry(main_frame, show="*", style='Modern.TEntry', width=40)
        password_entry.pack(fill='x', pady=(5, 20))
        password_entry.focus()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#1e1e2e')
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy,
                  style='Danger.TButton').pack(side='right', padx=(10, 0))
        
        def start_decrypt():
            password = password_entry.get()
            if not password:
                messagebox.showerror("Error", "Please enter a password!")
                return
            dialog.destroy()
            self.log_message("🔄 Starting decryption...")
            threading.Thread(target=self.decrypt_image_thread, 
                            args=(encrypted_path, password), daemon=True).start()
        
        ttk.Button(button_frame, text="🔓 Decrypt", command=start_decrypt,
                  style='Success.TButton').pack(side='right')
        
        # Enter key binding
        dialog.bind('<Return>', lambda e: start_decrypt())
        
    def decrypt_image_thread(self, encrypted_path, password):
        """Decrypt image in separate thread"""
        try:
            success = self.decrypt_image(encrypted_path, password)
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Decryption Successful", 
                                                              "Image decrypted successfully!\nRestored image is ready for viewing."))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Decryption failed: {e}"))
    
    def logout(self):
        """Logout and show auth window"""
        result = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if result:
            self.current_user = None
            self.show_auth_window()
        
    # Core encryption/decryption methods
    def generate_key(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def generate_random_password(self, length=16):
        """Generate a random password"""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    def send_email_with_attachment(self, receiver_email, subject, body, attachment_path=None):
        """Send email with optional attachment"""
        msg = EmailMessage()
        msg["From"] = PROJECT_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment_path and os.path.exists(attachment_path):
            mime_type, _ = mimetypes.guess_type(attachment_path)
            mime_type = mime_type or 'application/octet-stream'
            maintype, subtype = mime_type.split('/', 1)

            with open(attachment_path, 'rb') as file:
                msg.add_attachment(file.read(), maintype=maintype, subtype=subtype,
                                   filename=os.path.basename(attachment_path))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(PROJECT_EMAIL, APP_PASSWORD)
                smtp.send_message(msg)
            self.root.after(0, lambda: self.log_message("✅ Email sent successfully."))
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"❌ Failed to send email: {e}"))

    def encrypt_image(self, image_path: str, password: str, user_email: str):
        """Encrypt an image file"""
        with open(image_path, 'rb') as file:
            data = file.read()

        salt = os.urandom(16)
        key = self.generate_key(password, salt)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data)

        encrypted_path = image_path + '.encrypted'
        with open(encrypted_path, 'wb') as file:
            file.write(salt + encrypted_data)

        os.remove(image_path)
        
        self.root.after(0, lambda: self.log_message(f"✅ Image encrypted and saved as: {os.path.basename(encrypted_path)}"))

        # Save email info
        email_path = encrypted_path + ".email"
        with open(email_path, 'w') as f:
            f.write(user_email)

        # Send email with encrypted file and password
        subject = "🔐 Encrypted Image File with Password"
        body = (
            f"Hello {self.current_user['username']},\n\n"
            f"Your image '{os.path.basename(image_path)}' has been successfully encrypted.\n\n"
            f"The encrypted file is attached to this email.\n"
            f"Use the password below to decrypt it:\n\n"
            f"🔑 Password: {password}\n\n"
            f"Please keep this password safe and secure.\n\n"
            f"Best regards,\n"
            f"Image Encryption Tool"
        )
        self.send_email_with_attachment(user_email, subject, body, encrypted_path)

    def decrypt_image(self, encrypted_path: str, password: str):
        """Decrypt an image file"""
        email_path = encrypted_path + ".email"
        receiver_email = None
        if os.path.exists(email_path):
            with open(email_path, 'r') as f:
                receiver_email = f.read().strip()

        with open(encrypted_path, 'rb') as file:
            file_data = file.read()

        salt = file_data[:16]
        encrypted_data = file_data[16:]

        key = self.generate_key(password, salt)
        fernet = Fernet(key)

        try:
            decrypted_data = fernet.decrypt(encrypted_data)

            # Determine output path
            if encrypted_path.endswith(".encrypted"):
                output_path = encrypted_path[:-10]  # Remove .encrypted extension
            else:
                output_path = encrypted_path + "_restored"

            with open(output_path, 'wb') as file:
                file.write(decrypted_data)

            # Clean up encrypted files
            os.remove(encrypted_path)
            if os.path.exists(email_path):
                os.remove(email_path)

            self.root.after(0, lambda: self.log_message(f"✅ Image decrypted and restored as: {os.path.basename(output_path)}"))
            self.root.after(0, lambda: self.show_image_preview(output_path))

            # Send success email
            if receiver_email:
                subject = "✅ Image Decryption Successful"
                body = (
                    f"Hello {self.current_user['username']},\n\n"
                    f"Your encrypted image '{os.path.basename(output_path)}' has been successfully decrypted.\n\n"
                    f"The original image has been restored and is now available.\n\n"
                    f"Best regards,\n"
                    f"Image Encryption Tool"
                )
                self.send_email_with_attachment(receiver_email, subject, body, output_path)
            
            return True

        except Exception as e:
            self.root.after(0, lambda: self.log_message("❌ Cannot decrypt the image due to wrong password!"))
            self.root.after(0, lambda: messagebox.showerror("Decryption Failed", 
                                                           "Cannot decrypt the image due to wrong password!"))
            
            # Send failure email
            if receiver_email:
                subject = "❌ Image Decryption Failed"
                body = (
                    f"Hello {self.current_user['username']},\n\n"
                    f"An attempt to decrypt '{os.path.basename(encrypted_path)}' failed due to an incorrect password.\n\n"
                    f"Please ensure you are using the correct password that was provided during encryption.\n\n"
                    f"Best regards,\n"
                    f"Image Encryption Tool"
                )
                self.send_email_with_attachment(receiver_email, subject, body)
            
            return False

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageEncryptionGUI()
    app.run()
                