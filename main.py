import tkinter as tk
from gui.main_window import MainWindow
from gui.login_window import LoginWindow

def main():
    # Show login window first
    login_window = LoginWindow()
    authenticated, role, user_id, username = login_window.get_credentials()
    
    if authenticated:
        # Start main application with the authenticated role and user info
        app = MainWindow(role=role, user_id=user_id, username=username)
        app.mainloop()

if __name__ == "__main__":
    main()
