from datetime import date, timedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt

class ChartWidget(QWidget):
    """Base chart widget for displaying matplotlib figures in PyQt5."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def clear(self):
        self.figure.clear()
        self.canvas.draw()

def create_daily_chart(expenses_data):
    """Create a daily expenses chart."""
    figure = Figure(figsize=(8, 5), dpi=100)
    ax = figure.add_subplot(111)

    # Group by date
    daily_totals = {}
    for expense in expenses_data:
        exp_date = expense["date"]
        daily_totals[exp_date] = daily_totals.get(exp_date, 0) + expense["amount"]

    dates = sorted(daily_totals.keys())[-30:]  # Last 30 days
    amounts = [daily_totals[d] for d in dates]

    ax.bar(dates, amounts, color="#3b82f6", alpha=0.8)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Amount ($)", fontsize=10)
    ax.set_title("Daily Expenses", fontsize=12, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    figure.tight_layout()

    return figure

def create_category_pie_chart(category_data):
    """Create a pie chart for expense categories."""
    figure = Figure(figsize=(8, 6), dpi=100)
    ax = figure.add_subplot(111)

    if not category_data:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return figure

    categories = list(category_data.keys())
    amounts = list(category_data.values())
    colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#14b8a6"]

    ax.pie(amounts, labels=categories, autopct="%1.1f%%", colors=colors[:len(categories)], startangle=90)
    ax.set_title("Expenses by Category", fontsize=12, fontweight="bold")

    return figure

def create_monthly_chart(expenses_data):
    """Create a monthly expenses chart."""
    figure = Figure(figsize=(8, 5), dpi=100)
    ax = figure.add_subplot(111)

    # Group by month
    monthly_totals = {}
    for expense in expenses_data:
        exp_date = expense["date"][:7]  # YYYY-MM
        monthly_totals[exp_date] = monthly_totals.get(exp_date, 0) + expense["amount"]

    months = sorted(monthly_totals.keys())[-12:]  # Last 12 months
    amounts = [monthly_totals[m] for m in months]

    ax.bar(months, amounts, color="#10b981", alpha=0.8)
    ax.set_xlabel("Month", fontsize=10)
    ax.set_ylabel("Amount ($)", fontsize=10)
    ax.set_title("Monthly Expenses", fontsize=12, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    figure.tight_layout()

    return figure

def create_comparison_chart(expense_types):
    """Create a comparison chart."""
    figure = Figure(figsize=(8, 5), dpi=100)
    ax = figure.add_subplot(111)

    names = list(expense_types.keys())
    values = list(expense_types.values())
    colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"]

    ax.bar(names, values, color=colors[:len(names)], alpha=0.8)
    ax.set_ylabel("Amount ($)", fontsize=10)
    ax.set_title("Expense Comparison", fontsize=12, fontweight="bold")
    ax.tick_params(axis='x', rotation=45)
    figure.tight_layout()

    return figure
