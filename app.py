import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            type TEXT,
            date TEXT
        )
    """)
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    transactions = conn.execute("SELECT * FROM transactions").fetchall()

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_month = now.strftime("%Y-%m")
    current_year = now.strftime("%Y")

    daily = [t for t in transactions if t[4] == today]
    monthly = [t for t in transactions if t[4].startswith(current_month)]
    yearly = [t for t in transactions if t[4].startswith(current_year)]

    def calculate(data):
        income = sum(t[1] for t in data if t[3] == "income")
        expense = sum(t[1] for t in data if t[3] == "expense")
        savings = income - expense
        savings_rate = (savings / income * 100) if income else 0
        return income, expense, savings, round(savings_rate, 2)

    daily_stats = calculate(daily)
    monthly_stats = calculate(monthly)
    yearly_stats = calculate(yearly)

    # Monthly category breakdown
    category_totals = {}
    for t in monthly:
        if t[3] == "expense":
            category_totals[t[2]] = category_totals.get(t[2], 0) + t[1]

    # Smart suggestion logic
    income, expense, savings, savings_rate = monthly_stats

    if income == 0:
        suggestion = "Add your income to start tracking finances."
    elif savings_rate < 10:
        suggestion = "Your savings rate is low. Reduce discretionary spending like entertainment and shopping."
    elif 10 <= savings_rate < 25:
        suggestion = "Good start. Consider recurring deposits or fixed savings plans."
    elif 25 <= savings_rate < 40:
        suggestion = "Strong savings rate. You can explore SIP mutual funds."
    else:
        suggestion = "Excellent savings. Consider diversified investments (Equity + Debt portfolio)."

    conn.close()

    return render_template(
        "index.html",
        daily=daily_stats,
        monthly=monthly_stats,
        yearly=yearly_stats,
        category_totals=category_totals,
        suggestion=suggestion
    )

@app.route("/add", methods=["POST"])
def add():
    amount = float(request.form["amount"])
    category = request.form["category"]
    txn_type = request.form["type"]
    date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect("database.db")
    conn.execute(
        "INSERT INTO transactions (amount, category, type, date) VALUES (?, ?, ?, ?)",
        (amount, category, txn_type, date)
    )
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)