import sys
from datetime import date, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTabWidget, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox, QSpinBox,
                             QDateEdit, QTimeEdit, QMessageBox, QDialog, QScrollArea)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont
from scripts.supabase_db import SupabaseDatabase
from scripts.login_dialog import LoginDialog
from scripts.charts import (create_daily_chart, create_category_pie_chart,
                            create_monthly_chart, create_comparison_chart, ChartWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "INR": "₹",
    "AUD": "A$",
    "CAD": "C$",
    "CHF": "CHF",
    "CNY": "¥",
    "SEK": "kr",
    "NZD": "NZ$",
    "MXN": "$",
    "SGD": "S$",
    "HKD": "HK$",
    "NOK": "kr",
    "KRW": "₩",
    "TRY": "₺",
    "RUB": "₽",
    "BRL": "R$",
    "ZAR": "R"
}

AVAILABLE_CURRENCIES = list(CURRENCY_SYMBOLS.keys())

class AddExpenseDialog(QDialog):
    """Dialog for adding/editing expenses."""

    def __init__(self, parent=None, categories=None, expense_data=None, currency="USD"):
        super().__init__(parent)
        self.expense_data = expense_data
        self.categories = categories or []
        self.currency = currency
        self.currency_symbol = CURRENCY_SYMBOLS.get(currency, "$")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Expense" if not self.expense_data else "Edit Expense")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        # Amount with currency symbol
        layout.addWidget(QLabel(f"Amount ({self.currency_symbol}):"))
        self.amount_input = QLineEdit()
        if self.expense_data:
            self.amount_input.setText(str(self.expense_data.get("amount", "")))
        layout.addWidget(self.amount_input)

        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(self.categories)
        if self.expense_data:
            self.category_combo.setCurrentText(self.expense_data.get("category", ""))
        layout.addWidget(self.category_combo)

        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        if self.expense_data:
            self.description_input.setText(self.expense_data.get("description", ""))
        layout.addWidget(self.description_input)

        # Date
        layout.addWidget(QLabel("Date:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        if self.expense_data:
            self.date_input.setDate(QDate.fromString(self.expense_data.get("date", ""), "yyyy-MM-dd"))
        layout.addWidget(self.date_input)

        # Time
        layout.addWidget(QLabel("Time:"))
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        if self.expense_data:
            self.time_input.setTime(QTime.fromString(self.expense_data.get("time", ""), "hh:mm:ss"))
        layout.addWidget(self.time_input)

        # Payment Method
        layout.addWidget(QLabel("Payment Method:"))
        self.payment_method_input = QLineEdit()
        if self.expense_data:
            self.payment_method_input.setText(self.expense_data.get("payment_method", ""))
        layout.addWidget(self.payment_method_input)

        # Transaction ID
        layout.addWidget(QLabel("Transaction ID:"))
        self.transaction_id_input = QLineEdit()
        if self.expense_data:
            self.transaction_id_input.setText(self.expense_data.get("transaction_id", ""))
        layout.addWidget(self.transaction_id_input)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_data(self):
        """Get the expense data from inputs."""
        try:
            return {
                "amount": float(self.amount_input.text()),
                "category": self.category_combo.currentText(),
                "description": self.description_input.text(),
                "date": self.date_input.date().toString("yyyy-MM-dd"),
                "time": self.time_input.time().toString("hh:mm:ss"),
                "payment_method": self.payment_method_input.text(),
                "transaction_id": self.transaction_id_input.text()
            }
        except ValueError:
            return None

class ExpenseTrackerApp(QMainWindow):
    """Main application window."""

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.user_id = user["id"]
        self.db = SupabaseDatabase()
        self.currency = self.db.get_user_currency(self.user_id)
        self.currency_symbol = CURRENCY_SYMBOLS.get(self.currency, "$")
        self.categories = self.db.get_categories(self.user_id)
        if not self.categories:
            self.init_default_categories()
        self.init_ui()
        self.load_expenses()

    def init_default_categories(self):
        """Initialize default categories."""
        default_categories = [
            ("Food & Dining", "#F87171"),
            ("Transportation", "#60A5FA"),
            ("Shopping", "#A78BFA"),
            ("Entertainment", "#FBBF24"),
            ("Bills & Utilities", "#34D399"),
            ("Healthcare", "#FB7185"),
            ("Other", "#9CA3AF")
        ]
        for category, color in default_categories:
            self.db.add_category(self.user_id, category, color)
        self.categories = [cat for cat, _ in default_categories]

    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(f"Personal Expense Tracker - {self.user['username']}")
        self.setGeometry(50, 50, 1000, 700)

        # Main widget
        main_widget = QWidget()
        layout = QVBoxLayout()

        # Header with logout and currency selector
        header_layout = QHBoxLayout()
        welcome_label = QLabel(f"Welcome, {self.user['username']}!")
        welcome_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        currency_label = QLabel("Currency:")
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(AVAILABLE_CURRENCIES)
        self.currency_combo.setCurrentText(self.currency)
        self.currency_combo.currentTextChanged.connect(self.change_currency)
        self.currency_combo.setMaximumWidth(100)

        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)

        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(currency_label)
        header_layout.addWidget(self.currency_combo)
        header_layout.addWidget(logout_btn)
        layout.addLayout(header_layout)

        # Tab Widget
        tabs = QTabWidget()
        tabs.addTab(self.create_dashboard_tab(), "Dashboard")
        tabs.addTab(self.create_history_tab(), "History")
        tabs.addTab(self.create_analytics_tab(), "Analytics")
        tabs.addTab(self.create_search_tab(), "Search")

        layout.addWidget(tabs)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def change_currency(self, new_currency):
        """Change user's preferred currency."""
        if self.db.set_user_currency(self.user_id, new_currency):
            self.currency = new_currency
            self.currency_symbol = CURRENCY_SYMBOLS.get(new_currency, "$")
            self.load_expenses()  # Refresh all displays with new currency
        else:
            QMessageBox.warning(self, "Error", "Failed to change currency")

    def create_dashboard_tab(self):
        """Create dashboard tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Stats
        today_total = self.db.get_daily_total(self.user_id, date.today())
        weekly_total = self.db.get_weekly_total(self.user_id)
        monthly_total = self.db.get_monthly_total(self.user_id)

        stats_layout = QHBoxLayout()

        today_label = QLabel(f"Today: {self.currency_symbol}{today_total:.2f}")
        today_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3b82f6;")

        weekly_label = QLabel(f"This Week: {self.currency_symbol}{weekly_total:.2f}")
        weekly_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #10b981;")

        monthly_label = QLabel(f"This Month: {self.currency_symbol}{monthly_total:.2f}")
        monthly_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #f59e0b;")

        stats_layout.addWidget(today_label)
        stats_layout.addWidget(weekly_label)
        stats_layout.addWidget(monthly_label)
        stats_layout.addStretch()

        layout.addLayout(stats_layout)

        # Recent expenses
        layout.addWidget(QLabel("Recent Expenses"))
        self.dashboard_table = QTableWidget()
        self.dashboard_table.setColumnCount(6)
        self.dashboard_table.setHorizontalHeaderLabels(["Date", "Time", "Category", "Description", "Amount", "Payment Method"])
        self.refresh_dashboard_table()
        layout.addWidget(self.dashboard_table)

        # Add expense button
        add_btn = QPushButton("Add Expense")
        add_btn.clicked.connect(self.add_expense)
        layout.addWidget(add_btn)

        widget.setLayout(layout)
        return widget

    def create_history_tab(self):
        """Create history tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))
        self.history_category_combo = QComboBox()
        self.history_category_combo.addItem("All")
        self.history_category_combo.addItems(self.categories)
        self.history_category_combo.currentTextChanged.connect(self.refresh_history_table)
        filter_layout.addWidget(self.history_category_combo)

        filter_layout.addWidget(QLabel("From Date:"))
        self.history_from_date = QDateEdit()
        self.history_from_date.setDate(QDate.currentDate().addMonths(-1))
        self.history_from_date.dateChanged.connect(self.refresh_history_table)
        filter_layout.addWidget(self.history_from_date)

        filter_layout.addWidget(QLabel("To Date:"))
        self.history_to_date = QDateEdit()
        self.history_to_date.setDate(QDate.currentDate())
        self.history_to_date.dateChanged.connect(self.refresh_history_table)
        filter_layout.addWidget(self.history_to_date)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels(["Date", "Time", "Category", "Description", "Amount", "Payment Method", "Transaction ID", "Actions"])
        self.refresh_history_table()
        layout.addWidget(self.history_table)

        # Action buttons
        action_layout = QHBoxLayout()
        add_btn = QPushButton("Add Expense")
        add_btn.clicked.connect(self.add_expense)
        action_layout.addWidget(add_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        widget.setLayout(layout)
        return widget

    def create_analytics_tab(self):
        """Create analytics tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Chart selection
        chart_layout = QHBoxLayout()
        chart_layout.addWidget(QLabel("View:"))
        chart_combo = QComboBox()
        chart_combo.addItems(["Daily", "Monthly", "By Category"])
        chart_combo.currentTextChanged.connect(lambda: self.update_chart(chart_combo.currentText(), layout))
        chart_layout.addWidget(chart_combo)
        chart_layout.addStretch()
        layout.addLayout(chart_layout)

        # Chart container
        self.chart_container = QVBoxLayout()
        layout.addLayout(self.chart_container)

        # Initial chart
        self.update_chart("Daily", layout)

        widget.setLayout(layout)
        return widget

    def create_search_tab(self):
        """Create search tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Search filters
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search description or transaction ID...")
        search_layout.addWidget(self.search_input)

        search_layout.addWidget(QLabel("Category:"))
        self.search_category_combo = QComboBox()
        self.search_category_combo.addItem("All")
        self.search_category_combo.addItems(self.categories)
        search_layout.addWidget(self.search_category_combo)

        search_layout.addWidget(QLabel("Min Amount:"))
        self.search_min_amount = QSpinBox()
        self.search_min_amount.setMaximum(1000000)
        search_layout.addWidget(self.search_min_amount)

        search_layout.addWidget(QLabel("Max Amount:"))
        self.search_max_amount = QSpinBox()
        self.search_max_amount.setValue(100000)
        self.search_max_amount.setMaximum(1000000)
        search_layout.addWidget(self.search_max_amount)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Results table
        self.search_table = QTableWidget()
        self.search_table.setColumnCount(7)
        self.search_table.setHorizontalHeaderLabels(["Date", "Time", "Category", "Description", "Amount", "Payment Method", "Transaction ID"])
        layout.addWidget(self.search_table)

        widget.setLayout(layout)
        return widget

    def add_expense(self):
        """Add a new expense."""
        dialog = AddExpenseDialog(self, self.categories, currency=self.currency)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                if self.db.add_expense(
                        self.user_id,
                        data["amount"],
                        data["category"],
                        data["description"],
                        data["date"],
                        data["time"],
                        data["payment_method"],
                        data["transaction_id"]
                ):
                    QMessageBox.information(self, "Success", "Expense added successfully!")
                    self.load_expenses()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add expense")
            else:
                QMessageBox.warning(self, "Error", "Invalid amount entered")

    def load_expenses(self):
        """Load all expenses."""
        self.refresh_dashboard_table()
        self.refresh_history_table()

    def refresh_dashboard_table(self):
        """Refresh dashboard table with recent expenses."""
        expenses = self.db.get_recent_expenses(self.user_id, 10)
        self.dashboard_table.setRowCount(len(expenses))

        for row, expense in enumerate(expenses):
            self.dashboard_table.setItem(row, 0, QTableWidgetItem(expense.get("date", "")))
            self.dashboard_table.setItem(row, 1, QTableWidgetItem(expense.get("time", "")))
            self.dashboard_table.setItem(row, 2, QTableWidgetItem(expense.get("category", "")))
            self.dashboard_table.setItem(row, 3, QTableWidgetItem(expense.get("description", "")))
            self.dashboard_table.setItem(row, 4, QTableWidgetItem(f"{self.currency_symbol}{expense.get('amount', 0):.2f}"))
            self.dashboard_table.setItem(row, 5, QTableWidgetItem(expense.get("payment_method", "")))

    def refresh_history_table(self):
        """Refresh history table with filtered expenses."""
        category = self.history_category_combo.currentText()
        from_date = self.history_from_date.date().toPyDate()
        to_date = self.history_to_date.date().toPyDate()

        if category == "All":
            expenses = self.db.get_expenses_by_date_range(self.user_id, from_date, to_date)
        else:
            expenses = self.db.get_expenses_by_date_range(self.user_id, from_date, to_date)
            expenses = [e for e in expenses if e.get("category") == category]

        self.history_table.setRowCount(len(expenses))

        for row, expense in enumerate(expenses):
            self.history_table.setItem(row, 0, QTableWidgetItem(expense.get("date", "")))
            self.history_table.setItem(row, 1, QTableWidgetItem(expense.get("time", "")))
            self.history_table.setItem(row, 2, QTableWidgetItem(expense.get("category", "")))
            self.history_table.setItem(row, 3, QTableWidgetItem(expense.get("description", "")))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{self.currency_symbol}{expense.get('amount', 0):.2f}"))
            self.history_table.setItem(row, 5, QTableWidgetItem(expense.get("payment_method", "")))
            self.history_table.setItem(row, 6, QTableWidgetItem(expense.get("transaction_id", "")))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, exp_id=expense["id"]: self.delete_expense(exp_id))
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            self.history_table.setCellWidget(row, 7, action_widget)

    def perform_search(self):
        """Perform search on expenses."""
        query = self.search_input.text()
        category = self.search_category_combo.currentText()
        min_amount = self.search_min_amount.value()
        max_amount = self.search_max_amount.value()

        if category == "All":
            category = ""

        expenses = self.db.search_expenses(self.user_id, query, category, min_amount, max_amount)

        self.search_table.setRowCount(len(expenses))

        for row, expense in enumerate(expenses):
            self.search_table.setItem(row, 0, QTableWidgetItem(expense.get("date", "")))
            self.search_table.setItem(row, 1, QTableWidgetItem(expense.get("time", "")))
            self.search_table.setItem(row, 2, QTableWidgetItem(expense.get("category", "")))
            self.search_table.setItem(row, 3, QTableWidgetItem(expense.get("description", "")))
            self.search_table.setItem(row, 4, QTableWidgetItem(f"{self.currency_symbol}{expense.get('amount', 0):.2f}"))
            self.search_table.setItem(row, 5, QTableWidgetItem(expense.get("payment_method", "")))
            self.search_table.setItem(row, 6, QTableWidgetItem(expense.get("transaction_id", "")))

    def delete_expense(self, expense_id):
        """Delete an expense."""
        reply = QMessageBox.question(self, "Confirm", "Delete this expense?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db.delete_expense(expense_id):
                QMessageBox.information(self, "Success", "Expense deleted!")
                self.load_expenses()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete expense")

    def update_chart(self, chart_type, parent_layout):
        """Update the displayed chart."""
        # Clear previous chart
        while self.chart_container.count():
            self.chart_container.takeAt(0).widget().deleteLater()

        expenses = self.db.get_expenses(self.user_id, limit=1000)

        if chart_type == "Daily":
            figure = create_daily_chart(expenses)
        elif chart_type == "Monthly":
            figure = create_monthly_chart(expenses)
        else:  # By Category
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            category_data = self.db.get_expenses_by_category_for_period(self.user_id, start_date, end_date)
            figure = create_category_pie_chart(category_data)

        canvas = FigureCanvas(figure)
        self.chart_container.addWidget(canvas)

    def logout(self):
        """Logout and return to login screen."""
        self.close()

def main():
    app = QApplication(sys.argv)

    # Show login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        user = login_dialog.current_user
        tracker_app = ExpenseTrackerApp(user)
        tracker_app.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
