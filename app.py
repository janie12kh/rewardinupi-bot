from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_super_secret_key"

DATABASE = "../bot/bot.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/")
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return render_template("dashboard.html", users=users)

@app.route("/withdrawals")
def withdrawals():
    if not session.get("admin"):
        return redirect("/")
    db = get_db()
    requests = db.execute("SELECT * FROM withdrawals WHERE status='pending'").fetchall()
    return render_template("withdrawals.html", requests=requests)

@app.route("/approve/<int:user_id>")
def approve(user_id):
    db = get_db()
    db.execute("UPDATE withdrawals SET status='approved' WHERE user_id=? AND status='pending'", (user_id,))
    db.commit()
    return redirect("/withdrawals")

@app.route("/reject/<int:user_id>")
def reject(user_id):
    db = get_db()
    rows = db.execute("SELECT amount FROM withdrawals WHERE user_id=? AND status='pending'", (user_id,)).fetchall()
    refund = sum([row["amount"] for row in rows])
    db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (refund, user_id))
    db.execute("UPDATE withdrawals SET status='rejected' WHERE user_id=? AND status='pending'", (user_id,))
    db.commit()
    return redirect("/withdrawals")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
