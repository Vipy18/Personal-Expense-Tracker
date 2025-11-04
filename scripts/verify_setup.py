import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print(f"[✓] Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("[✗] ERROR: Python 3.8+ required")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("[✗] ERROR: .env file not found")
        print("   Create .env file with:")
        print("   SUPABASE_URL=your-url")
        print("   SUPABASE_ANON_KEY=your-key")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        print("[✗] ERROR: Missing environment variables in .env")
        return False

    print("[✓] Environment variables loaded")
    return True

def check_dependencies():
    """Check if all required packages are installed."""
    required = {
        "PyQt5": "5.15+",
        "matplotlib": "3.8+",
        "supabase": "2.5+",
        "dotenv": "1.0+"
    }

    for package, version in required.items():
        try:
            if package == "dotenv":
                __import__("dotenv")
            else:
                __import__(package.lower().replace("-", "_"))
            print(f"[✓] {package} installed")
        except ImportError:
            print(f"[✗] ERROR: {package} not installed")
            return False

    return True

def check_supabase_connection():
    """Test Supabase connection."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from scripts.supabase_db import SupabaseDatabase

        db = SupabaseDatabase()
        print("[✓] Supabase connection successful")
        return True
    except Exception as e:
        print(f"[✗] ERROR: Supabase connection failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Personal Expense Tracker - Setup Verification")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Supabase Connection", check_supabase_connection),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n[*] Checking {name}...")
        if not check_func():
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[✓] All checks passed! Ready to run.")
        print("\nRun: python main.py")
    else:
        print("[✗] Some checks failed. See errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
