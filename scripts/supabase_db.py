import os
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseDatabase:
    def __init__(self):
        """Initialize Supabase client using REST API."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables.\n"
                "Please create a .env file in the project root with:\n"
                "  SUPABASE_URL=https://your-project.supabase.co\n"
                "  SUPABASE_ANON_KEY=your-anon-key-here\n\n"
                "Get these from: https://app.supabase.com → Settings → API"
            )

        # Ensure URL doesn't have trailing slash
        self.supabase_url = self.supabase_url.rstrip('/')
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }

        print("[v0] Supabase REST API client initialized successfully")

    def _make_request(self, method: str, table: str, filters: str = "", data: Dict = None) -> Optional[List[Dict]]:
        """Make a request to Supabase REST API."""
        url = f"{self.supabase_url}/rest/v1/{table}{filters}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                return None

            if response.status_code in [200, 201]:
                try:
                    return response.json() if response.text else True
                except:
                    return True
            else:
                print(f"[v0] API Error {response.status_code}: {response.text}")
                try:
                    error_data = response.json()
                    print(f"[v0] Error details: {json.dumps(error_data, indent=2)}")
                except:
                    pass
                return None

        except Exception as e:
            print(f"[v0] Request error: {str(e)}")
            import traceback
            print(f"[v0] Traceback: {traceback.format_exc()}")
            return None

    def register_user(self, username: str, password: str, email: str = "") -> bool:
        """Register a new user."""
        from scripts.auth_utils import hash_password

        try:
            print(f"[v0] Starting registration for username: {username}")

            # Check if user already exists
            filters = f"?username=eq.{username}"
            existing = self._make_request("GET", "users", filters)
            print(f"[v0] Username check result: {existing}")

            if isinstance(existing, list) and len(existing) > 0:
                print(f"[v0] User already exists: {username}")
                return False

            print(f"[v0] Username available, proceeding with registration")

            # Hash password
            password_hash, salt = hash_password(password)
            print(f"[v0] Password hashed successfully")

            # Insert new user
            insert_data = {
                "username": username,
                "password_hash": password_hash,
                "password_salt": salt,
                "email": email if email else None
            }

            print(f"[v0] Inserting user: {username}")
            print(f"[v0] Insert data: {insert_data}")
            result = self._make_request("POST", "users", data=insert_data)

            if result is True or (isinstance(result, list) and len(result) > 0):
                print(f"[v0] User registered successfully: {username}")
                return True
            else:
                print(f"[v0] Failed to insert user - result: {result}")
                return False

        except Exception as e:
            print(f"[v0] Registration error: {str(e)}")
            import traceback
            print(f"[v0] Full traceback:\n{traceback.format_exc()}")
            return False

    def login_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data if successful."""
        from scripts.auth_utils import verify_password

        try:
            filters = f"?username=eq.{username}"
            result = self._make_request("GET", "users", filters)

            if not result or len(result) == 0:
                return None

            user = result[0]
            if verify_password(user["password_hash"], user["password_salt"], password):
                return user
            return None
        except Exception as e:
            print(f"[v0] Login error: {e}")
            return None

    def add_expense(self, user_id: str, amount: float, category: str,
                    description: str, date_str: str, time_str: str,
                    payment_method: str = "", transaction_id: str = "") -> bool:
        """Add a new expense."""
        try:
            data = {
                "user_id": user_id,
                "amount": amount,
                "category": category,
                "description": description,
                "date": date_str,
                "time": time_str,
                "payment_method": payment_method,
                "transaction_id": transaction_id
            }
            result = self._make_request("POST", "expenses", data=data)
            return result is not None
        except Exception as e:
            print(f"[v0] Error adding expense: {e}")
            return False

    def get_expenses(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all expenses for a user."""
        try:
            filters = f"?user_id=eq.{user_id}&limit={limit}&order=date.desc"
            result = self._make_request("GET", "expenses", filters)
            return result if result else []
        except Exception as e:
            print(f"[v0] Error fetching expenses: {e}")
            return []

    def get_recent_expenses(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent expenses for a user."""
        try:
            filters = f"?user_id=eq.{user_id}&limit={limit}&order=date.desc,time.desc"
            result = self._make_request("GET", "expenses", filters)
            return result if result else []
        except Exception as e:
            print(f"[v0] Error fetching recent expenses: {e}")
            return []

    def update_expense(self, expense_id: str, **kwargs) -> bool:
        """Update an expense."""
        try:
            filters = f"?id=eq.{expense_id}"
            result = self._make_request("PATCH", "expenses", filters, kwargs)
            return result is not None
        except Exception as e:
            print(f"[v0] Error updating expense: {e}")
            return False

    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense."""
        try:
            filters = f"?id=eq.{expense_id}"
            result = self._make_request("DELETE", "expenses", filters)
            return result is not None
        except Exception as e:
            print(f"[v0] Error deleting expense: {e}")
            return False

    def get_expenses_by_date_range(self, user_id: str, start_date: date, end_date: date) -> List[Dict]:
        """Get expenses within a date range."""
        try:
            filters = f"?user_id=eq.{user_id}&date=gte.{str(start_date)}&date=lte.{str(end_date)}&order=date.desc"
            result = self._make_request("GET", "expenses", filters)
            return result if result else []
        except Exception as e:
            print(f"[v0] Error fetching expenses by date range: {e}")
            return []

    def get_expenses_by_category(self, user_id: str, category: str) -> List[Dict]:
        """Get expenses for a specific category."""
        try:
            filters = f"?user_id=eq.{user_id}&category=eq.{category}&order=date.desc"
            result = self._make_request("GET", "expenses", filters)
            return result if result else []
        except Exception as e:
            print(f"[v0] Error fetching expenses by category: {e}")
            return []

    def search_expenses(self, user_id: str, query: str = "", category: str = "",
                        min_amount: float = 0, max_amount: float = float('inf')) -> List[Dict]:
        """Search expenses by description, category, and amount."""
        try:
            filters = f"?user_id=eq.{user_id}&amount=gte.{min_amount}&amount=lte.{max_amount}&order=date.desc"

            if category:
                filters += f"&category=eq.{category}"

            result = self._make_request("GET", "expenses", filters)

            # Filter by description/transaction_id if query provided
            if query and result:
                query_lower = query.lower()
                result = [
                    e for e in result
                    if query_lower in e.get("description", "").lower()
                       or query_lower in e.get("transaction_id", "").lower()
                ]

            return result if result else []
        except Exception as e:
            print(f"[v0] Error searching expenses: {e}")
            return []

    def get_daily_total(self, user_id: str, target_date: date) -> float:
        """Get total expenses for a specific day."""
        try:
            expenses = self.get_expenses_by_date_range(user_id, target_date, target_date)
            return sum(e["amount"] for e in expenses)
        except Exception as e:
            print(f"[v0] Error calculating daily total: {e}")
            return 0.0

    def get_weekly_total(self, user_id: str, target_date: date = None) -> float:
        """Get total expenses for the current week."""
        if target_date is None:
            target_date = date.today()

        try:
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=6)
            expenses = self.get_expenses_by_date_range(user_id, start_date, end_date)
            return sum(e["amount"] for e in expenses)
        except Exception as e:
            print(f"[v0] Error calculating weekly total: {e}")
            return 0.0

    def get_monthly_total(self, user_id: str, target_date: date = None) -> float:
        """Get total expenses for the current month."""
        if target_date is None:
            target_date = date.today()

        try:
            start_date = date(target_date.year, target_date.month, 1)
            if target_date.month == 12:
                end_date = date(target_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)

            expenses = self.get_expenses_by_date_range(user_id, start_date, end_date)
            return sum(e["amount"] for e in expenses)
        except Exception as e:
            print(f"[v0] Error calculating monthly total: {e}")
            return 0.0

    def get_yearly_total(self, user_id: str, year: int = None) -> float:
        """Get total expenses for a specific year."""
        if year is None:
            year = date.today().year

        try:
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            expenses = self.get_expenses_by_date_range(user_id, start_date, end_date)
            return sum(e["amount"] for e in expenses)
        except Exception as e:
            print(f"[v0] Error calculating yearly total: {e}")
            return 0.0

    def get_expenses_by_category_for_period(self, user_id: str, start_date: date, end_date: date) -> Dict[str, float]:
        """Get expenses grouped by category for a date range."""
        try:
            expenses = self.get_expenses_by_date_range(user_id, start_date, end_date)
            category_totals = {}
            for expense in expenses:
                category = expense["category"]
                category_totals[category] = category_totals.get(category, 0) + expense["amount"]
            return category_totals
        except Exception as e:
            print(f"[v0] Error getting category breakdown: {e}")
            return {}

    def get_categories(self, user_id: str) -> List[str]:
        """Get all categories for a user."""
        try:
            filters = f"?user_id=eq.{user_id}"
            result = self._make_request("GET", "categories", filters)
            return [cat["name"] for cat in result] if result else []
        except Exception as e:
            print(f"[v0] Error fetching categories: {e}")
            return []

    def add_category(self, user_id: str, name: str, color: str = "#3B82F6") -> bool:
        """Add a new category for a user."""
        try:
            data = {
                "user_id": user_id,
                "name": name,
                "color": color
            }
            result = self._make_request("POST", "categories", data=data)
            return result is not None
        except Exception as e:
            print(f"[v0] Error adding category: {e}")
            return False

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by ID."""
        try:
            filters = f"?id=eq.{user_id}"
            result = self._make_request("GET", "users", filters)
            return result[0] if result else None
        except Exception as e:
            print(f"[v0] Error fetching user: {e}")
            return None

    def set_user_currency(self, user_id: str, currency: str) -> bool:
        """Set user's preferred currency."""
        try:
            filters = f"?id=eq.{user_id}"
            result = self._make_request("PATCH", "users", filters, {"currency": currency})
            return result is not None
        except Exception as e:
            print(f"[v0] Error setting currency: {e}")
            return False

    def get_user_currency(self, user_id: str) -> str:
        """Get user's preferred currency (default USD)."""
        try:
            user = self.get_user_by_id(user_id)
            return user.get("currency", "USD") if user else "USD"
        except Exception as e:
            print(f"[v0] Error fetching currency: {e}")
            return "USD"
