import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cinema Management System - Login")
        self.geometry("400x350")
        self.resizable(False, False)
        
        self.selected_role = None
        self.authenticated = False
        self.user_id = None
        self.username = None  # Add username attribute to track authenticated username
        
        # Create login form
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Login to Cinema Management System", font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)
        
        # Role selection
        role_frame = ttk.LabelFrame(main_frame, text="Select Role")
        role_frame.pack(fill="x", pady=10)
        
        self.role_var = tk.StringVar(value="admin_user")
        
        # Add only admin and clerk roles
        roles = [("Administrator", "admin_user"), ("Ticket Clerk", "clerk_user")]
        for idx, (role_name, role_value) in enumerate(roles):
            ttk.Radiobutton(role_frame, text=role_name, value=role_value, 
                           variable=self.role_var).pack(anchor="w", padx=10, pady=5)
        
        # Username field
        ttk.Label(main_frame, text="Username:").pack(anchor="w", pady=(10, 5))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var)
        self.username_entry.pack(fill="x")
        
        # Password field
        ttk.Label(main_frame, text="Password:").pack(anchor="w", pady=(10, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*")
        self.password_entry.pack(fill="x")
        
        # Login button
        login_button = ttk.Button(main_frame, text="Login", command=self.login)
        login_button.pack(pady=20)
        
    def login(self):
        """Attempt to login with the provided credentials"""
        username = self.username_var.get()
        password = self.password_var.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Username and password are required.")
            return
        
        try:
            # First check if user exists in Users table
            con = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port']
            )
            
            cursor = con.cursor(dictionary=True)
            # Query to check user credentials and get user_id
            query = "SELECT UserID, Username, Role FROM Users WHERE Username = %s AND PasswordHash = SHA2(%s, 256) AND Role = %s"
            cursor.execute(query, (username, password, 'Admin' if role == 'admin_user' else 'TicketClerk'))
            user = cursor.fetchone()
            cursor.close()
            con.close()
            
            if user:
                self.authenticated = True
                self.selected_role = role
                self.user_id = user['UserID']
                self.username = user['Username']  # Store the username
                messagebox.showinfo("Login Success", f"Logged in as {user['Username']} ({user['Role']})")
                self.destroy()  # Close login window
            else:
                # Try connecting with MySQL user
                conn = mysql.connector.connect(
                    host=DB_CONFIG['host'],
                    user=role,
                    password=password,
                    database=DB_CONFIG['database'],
                    port=DB_CONFIG['port']
                )
                
                if conn.is_connected():
                    conn.close()
                    self.authenticated = True
                    self.selected_role = role
                    self.username = username  # Store the username for MySQL user
                    messagebox.showinfo("Login Success", f"Logged in as {role}")
                    self.destroy()  # Close login window
                else:
                    messagebox.showerror("Login Error", "Invalid username or password")
                    
        except mysql.connector.Error as e:
            messagebox.showerror("Login Error", f"Failed to login: {str(e)}")
            
    def get_credentials(self):
        """Return the authentication result, selected role, user_id, and username"""
        self.mainloop()  # Start the login window main loop
        return self.authenticated, self.selected_role, self.user_id, self.username
