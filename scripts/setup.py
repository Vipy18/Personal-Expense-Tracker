"""
Environment variable loader with .env support
"""
import os
import sys

def load_environment():
    """
    Load environment variables from .env file or system environment
    """
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"[INFO] Loaded environment from {env_file}")
        else:
            print(f"[INFO] No .env file found at {env_file}")
    except ImportError:
        print("[WARNING] python-dotenv not installed. Using system environment variables.")

    # Check if required variables are set
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print(f"\n[ERROR] Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these variables before running the app.")
        return False

    print("[SUCCESS] All environment variables are set!")
    return True

def create_env_template():
    """
    Create a template .env file if it doesn't exist
    """
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

    if not os.path.exists(env_file):
        template = """# Supabase Configuration
# Get these values from your Supabase project dashboard
# Go to Settings → API

SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_anon_key_here
"""
        with open(env_file, 'w') as f:
            f.write(template)
        print(f"[INFO] Created .env template at {env_file}")
        print("[INFO] Please fill in your Supabase credentials and try again.")
        return False

    return True