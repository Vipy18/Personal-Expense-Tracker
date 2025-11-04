import hashlib
import os
import secrets
from typing import Tuple
import json
from pathlib import Path
import base64

CREDENTIALS_FILE = Path.home() / ".expense_tracker_credentials"

def hash_password(password: str) -> Tuple[str, str]:
    """
    Hash a password using PBKDF2.
    Returns tuple of (hashed_password, salt)
    """
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return password_hash.hex(), salt

def verify_password(stored_hash: str, stored_salt: str, provided_password: str) -> bool:
    """
    Verify a provided password against stored hash and salt.
    """
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        stored_salt.encode('utf-8'),
        100000
    )
    return password_hash.hex() == stored_hash

def encrypt_credentials(username: str, password: str) -> str:
    """Encrypt credentials for storage (simple base64 - for local storage only)."""
    creds = f"{username}:{password}".encode('utf-8')
    return base64.b64encode(creds).decode('utf-8')

def decrypt_credentials(encrypted: str) -> tuple:
    """Decrypt stored credentials."""
    try:
        creds = base64.b64decode(encrypted.encode('utf-8')).decode('utf-8')
        username, password = creds.split(':', 1)
        return username, password
    except:
        return None, None

def save_credentials(username: str, password: str) -> None:
    """Save credentials to local file if user enables remember me."""
    encrypted = encrypt_credentials(username, password)
    try:
        CREDENTIALS_FILE.write_text(encrypted)
        CREDENTIALS_FILE.chmod(0o600)  # Read/write for owner only
    except Exception as e:
        print(f"[v0] Failed to save credentials: {e}")

def load_credentials() -> tuple:
    """Load saved credentials if they exist."""
    try:
        if CREDENTIALS_FILE.exists():
            encrypted = CREDENTIALS_FILE.read_text()
            return decrypt_credentials(encrypted)
    except Exception as e:
        print(f"[v0] Failed to load credentials: {e}")
    return None, None

def clear_credentials() -> None:
    """Clear saved credentials."""
    try:
        if CREDENTIALS_FILE.exists():
            CREDENTIALS_FILE.unlink()
    except Exception as e:
        print(f"[v0] Failed to clear credentials: {e}")
