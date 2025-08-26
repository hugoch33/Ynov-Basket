import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask_caching import Cache   

API_BASE = "https://api.balldontlie.io/v1"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["DATABASE"] = os.path.join(app.instance_path, "app.sqlite")
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes
    cache = Cache(app)

    def get_db():
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        conn = get_db()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        ''')
        conn.commit()
        conn.close()

    init_db()

    def login_required(view):
        from functools import wraps
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    @cache.memoize()
    def api_get(path, params=None):
        headers = {
            "Authorization": "ba5256e6-cd8c-442e-bcbe-ea4c80dc87c8"
        }
        try:
            r = requests.get(f"{API_BASE}{path}", params=params, headers=headers, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print("API error:", e)
            return None

    @app.get("/register")
    def register():
        return render_template("register.html")

    @app.post("/register")
    def register_post():
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not email or not password:
            flash("Email et mot de passe sont requis.", "error")
            return redirect(url_for("register"))
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users(email, password_hash, created_at) VALUES(?,?,?)",
                        (email, generate_password_hash(password), datetime.utcnow().isoformat()))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Cet email est déjà utilisé.", "error")
            conn.close()
            return redirect(url_for("register"))
        user_id = cur.lastrowid
        conn.close()
        session["user_id"] = user_id
        session["email"] = email
        return redirect(url_for("players"))

    @app.get("/login")
    def login():
        return render_template("login.html")

    @app.post("/login")
    def login_post():
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Identifiants invalides.", "error")
            return redirect(url_for("login"))
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        return redirect(url_for("players"))

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    def index():
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return redirect(url_for("players"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
