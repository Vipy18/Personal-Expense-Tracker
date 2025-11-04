"""
Troubleshooting script for common issues
"""
import os
import sys
from dotenv import load_dotenv
import os
from pathlib import Path

# Specify the path to your .env file
load_dotenv(dotenv_path = Path(__file__).parent.parent / '.env')

def print_section(title):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_env_file():
    """Check .env file setup"""
    print_section("1. Checking .env File")

    env_path = Path(__file__).parent.parent / '.env'

    if not env_path.exists():
        print("  ✗ .env file NOT found in project root")
        print(f"    Expected location: {env_path}")
        print("\n  To fix: Create .env file with:")
        print("    SUPABASE_URL=your-url")
        print("    SUPABASE_ANON_KEY=your-key")
        return False

    print(f"  ✓ .env file found at {env_path}")

    with open(env_path) as f:
        content = f.read()

    if 'SUPABASE_URL' not in content:
        print("  ✗ SUPABASE_URL not found in .env")
        return False

    if 'SUPABASE_ANON_KEY' not in content:
        print("  ✗ SUPABASE_ANON_KEY not found in .env")
        return False

    print("  ✓ Both credentials found in .env")

    # Check for common mistakes
    if 'SUPABASE_URL=' in content and content.split('SUPABASE_URL=')[1].split('\n')[0].strip().startswith('http'):
        print("  ✓ SUPABASE_URL appears valid (starts with http)")
    else:
        print("  ✗ SUPABASE_URL may be invalid")
        return False

    return True

def check_env_vars():
    """Check environment variables"""
    print_section("2. Checking Environment Variables")

    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_ANON_KEY')

    if url:
        print(f"  ✓ SUPABASE_URL is set")
        if url.startswith('https://'):
            print(f"    Value: {url[:50]}...")
        else:
            print("  ✗ SUPABASE_URL doesn't start with https://")
            return False
    else:
        print("  ✗ SUPABASE_URL not set")

    if key:
        print(f"  ✓ SUPABASE_ANON_KEY is set")
        print(f"    Value: {key[:20]}...{key[-10:]}")
    else:
        print("  ✗ SUPABASE_ANON_KEY not set")

    return bool(url and key)

def check_dependencies():
    """Check required packages"""
    print_section("3. Checking Dependencies")

    packages = {
        'PyQt5': 'PyQt5',
        'matplotlib': 'matplotlib',
        'supabase': 'supabase',
        'dotenv': 'dotenv'
    }

    all_ok = True
    for name, module in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name} installed")
        except ImportError:
            print(f"  ✗ {name} NOT installed")
            all_ok = False

    if not all_ok:
        print("\n  To fix: pip install -r requirements.txt")

    return all_ok

def check_project_files():
    """Check required project files"""
    print_section("4. Checking Project Files")

    required_files = {
        'main.py': 'Main application',
        'requirements.txt': 'Dependencies list',
        'scripts/supabase_db.py': 'Database module',
        'scripts/auth_utils.py': 'Authentication utilities',
        'scripts/login_dialog.py': 'Login UI',
        'scripts/charts.py': 'Charts module',
        'scripts/supabase_schema.sql': 'Database schema'
    }

    all_ok = True
    for file_path, description in required_files.items():
        path = Path(__file__).parent.parent / file_path
        if path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - {description} MISSING")
            all_ok = False

    return all_ok

def test_supabase_connection():
    """Test Supabase connection"""
    print_section("5. Testing Supabase Connection")

    try:
        from scripts.supabase_db import SupabaseDatabase

        print("  Attempting to connect...")
        db = SupabaseDatabase()
        print("  ✓ Successfully created Supabase client")

        # Try a simple query
        try:
            result = db.client.table('users').select('count', count='exact').execute()
            print("  ✓ Successfully queried database")
            return True
        except Exception as e:
            print(f"  ✗ Query failed: {str(e)}")
            print("\n  Possible causes:")
            print("    - Database schema not created (run supabase_schema.sql in Supabase)")
            print("    - Wrong credentials")
            print("    - Network connection issue")
            return False

    except Exception as e:
        print(f"  ✗ Connection failed: {str(e)}")
        print("\n  Possible causes:")
        print("    - Missing environment variables")
        print("    - Invalid URL or API key")
        return False

def main():
    print("=" * 60)
    print(" Personal Expense Tracker - Troubleshooting")
    print("=" * 60)

    results = {
        '.env file': check_env_file(),
        'Environment variables': check_env_vars(),
        'Dependencies': check_dependencies(),
        'Project files': check_project_files(),
        'Supabase connection': test_supabase_connection()
    }

    print_section("Summary")

    all_passed = True
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)

    if all_passed:
        print(" ✓ All checks PASSED - Ready to run!")
        print("\n Command: python main.py")
        return 0
    else:
        print(" ✗ Some checks FAILED - See details above")
        print("\n Quick fixes:")
        print("  1. Create .env file with SUPABASE_URL and SUPABASE_ANON_KEY")
        print("  2. Run: pip install -r requirements.txt")
        print("  3. In Supabase, run scripts/supabase_schema.sql")
        print("  4. Run this script again to verify")
        return 1

if __name__ == '__main__':
    sys.exit(main())