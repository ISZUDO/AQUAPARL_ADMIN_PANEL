from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔐 SECRET KEY (Render + local uchun safe)
app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")


# ---------------- LOGIN ----------------
USERNAME = "admin"
PASSWORD = "12345"


# ---------------- PLACES ----------------
male_places = list(range(10, 145))
female_places = list(range(1, 10)) + list(range(145, 189)) + list(range(201, 207))


# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place INTEGER,
            gender TEXT,
            start_time TEXT,
            end_time TEXT,
            vip INTEGER
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- CHECK STATUS ----------------
def get_place_status(place):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        SELECT end_time FROM bookings
        WHERE place = ?
        ORDER BY id DESC LIMIT 1
    """, (place,))

    row = c.fetchone()
    conn.close()

    if not row:
        return "free"

    end_time = datetime.fromisoformat(row[0])

    if datetime.now() >= end_time:
        return "expired"

    return "occupied"


# ---------------- CLEAN EXPIRED ----------------
def cleanup_expired():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT id, end_time FROM bookings")
    rows = c.fetchall()

    for r in rows:
        booking_id = r[0]
        end_time = datetime.fromisoformat(r[1])

        if datetime.now() >= end_time:
            c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

    conn.commit()
    conn.close()


# ---------------- LOGIN PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect("/dashboard")

        return "Login yoki parol xato!"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")

    male_data = [{"number": p, "status": get_place_status(p)} for p in male_places]
    female_data = [{"number": p, "status": get_place_status(p)} for p in female_places]

    return render_template(
        "dashboard.html",
        male_places=male_data,
        female_places=female_data
    )


# ---------------- OCCUPY PLACE ----------------
@app.route("/occupy", methods=["POST"])
def occupy():
    if not session.get("logged_in"):
        return redirect("/")

    place = int(request.form.get("place"))
    gender = request.form.get("gender")
    duration = request.form.get("duration")

    if get_place_status(place) == "occupied":
        return "Bu joy band!"

    start_time = datetime.now()

    if duration == "vip":
        end_time = start_time + timedelta(hours=5)
        vip = 1
    else:
        end_time = start_time + timedelta(hours=1, minutes=30)
        vip = 0

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO bookings (place, gender, start_time, end_time, vip)
        VALUES (?, ?, ?, ?, ?)
    """, (
        place,
        gender,
        start_time.isoformat(),
        end_time.isoformat(),
        vip
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- FREE PLACE ----------------
@app.route("/free/<int:place>")
def free_place(place):
    if not session.get("logged_in"):
        return redirect("/")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("DELETE FROM bookings WHERE place = ?", (place,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- STATUS API ----------------
@app.route("/status")
def status():
    cleanup_expired()

    data = {}

    for p in male_places + female_places:
        data[p] = get_place_status(p)

    return jsonify(data)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)