from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt
from scripts.supabase_db import SupabaseDatabase
from scripts.auth_utils import save_credentials, load_credentials, clear_credentials

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = SupabaseDatabase()
        self.current_user = None
        self.init_ui()
        self.load_saved_credentials()

    def init_ui(self):
        self.setWindowTitle("Expense Tracker - Login")
        self.setGeometry(100, 100, 400, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f4f6;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QTabWidget {
                border: none;
            }
            QCheckBox {
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Personal Expense Tracker")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Tab Widget
        tabs = QTabWidget()
        tabs.addTab(self.create_login_tab(), "Login")
        tabs.addTab(self.create_register_tab(), "Register")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_login_tab(self):
        """Create login tab UI."""
        widget = QDialog()
        layout = QVBoxLayout()

        # Username
        layout.addWidget(QLabel("Username:"))
        self.login_username = QLineEdit()
        layout.addWidget(self.login_username)

        # Password
        layout.addWidget(QLabel("Password:"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)

        self.remember_me_checkbox = QCheckBox("Remember me")
        self.remember_me_checkbox.setStyleSheet("margin-bottom: 10px;")
        layout.addWidget(self.remember_me_checkbox)

        # Login Button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        clear_btn = QPushButton("Clear Saved Login")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        clear_btn.clicked.connect(self.clear_saved_login)
        layout.addWidget(clear_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_register_tab(self):
        """Create registration tab UI."""
        widget = QDialog()
        layout = QVBoxLayout()

        # Username
        layout.addWidget(QLabel("Username (min 3 characters):"))
        self.reg_username = QLineEdit()
        layout.addWidget(self.reg_username)

        # Email
        layout.addWidget(QLabel("Email (optional):"))
        self.reg_email = QLineEdit()
        layout.addWidget(self.reg_email)

        # Password
        layout.addWidget(QLabel("Password (min 6 characters):"))
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_password)

        # Confirm Password
        layout.addWidget(QLabel("Confirm Password:"))
        self.reg_confirm_password = QLineEdit()
        self.reg_confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_confirm_password)

        # Register Button
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def load_saved_credentials(self):
        """Auto-load saved credentials if they exist."""
        username, password = load_credentials()
        if username and password:
            self.login_username.setText(username)
            self.login_password.setText(password)
            self.remember_me_checkbox.setChecked(True)

    def clear_saved_login(self):
        """Clear saved credentials."""
        reply = QMessageBox.question(self, "Confirm",
                                     "Clear saved login information?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            clear_credentials()
            self.login_username.clear()
            self.login_password.clear()
            self.remember_me_checkbox.setChecked(False)
            QMessageBox.information(self, "Success", "Saved login cleared.")

    def handle_login(self):
        """Handle login attempt."""
        username = self.login_username.text().strip()
        password = self.login_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return

        user = self.db.login_user(username, password)
        if user:
            self.current_user = user
            if self.remember_me_checkbox.isChecked():
                save_credentials(username, password)
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")
            self.login_password.clear()

    def handle_register(self):
        """Handle registration."""
        username = self.reg_username.text().strip()
        email = self.reg_email.text().strip()
        password = self.reg_password.text()
        confirm_password = self.reg_confirm_password.text()

        if not username:
            QMessageBox.warning(self, "Error", "Username cannot be empty")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Error", "Username must be at least 3 characters")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        try:
            print(f"[v0] Starting registration for: {username}")
            success = self.db.register_user(username, password, email)
            if success:
                QMessageBox.information(self, "Success", "Registration successful! Please login.")
                self.reg_username.clear()
                self.reg_email.clear()
                self.reg_password.clear()
                self.reg_confirm_password.clear()
            else:
                QMessageBox.warning(self, "Registration Failed",
                                    "Username already exists or registration failed.\n"
                                    "Check console output for details.")
                print(f"[v0] Registration returned False for: {username}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}\n\nCheck console for details.")
            print(f"[v0] Registration exception: {str(e)}")
            import traceback
            print(f"[v0] Full traceback:\n{traceback.format_exc()}")
