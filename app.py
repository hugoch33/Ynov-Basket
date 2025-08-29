import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask_caching import Cache   # <--- ajout

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
            cache_key = (path, tuple(sorted(params.items())) if params else None)
            
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

    @app.get("/players")
    @login_required
    def players():
        cursor = request.args.get("cursor", 0, type=int) 
        per_page = 24  

        resp = api_get(f"/players?per_page={per_page}&cursor={cursor}")
        if not resp or "data" not in resp:
            return render_template("players.html", players=[], meta=None, cursor=cursor, per_page=per_page)

        players = resp["data"]
        meta = resp.get("meta", {})

        print("=== META ===")
        print(meta)

        return render_template("players.html", players=players, meta=meta, cursor=cursor, per_page=per_page)



    @app.get("/player/<int:player_id>")
    @login_required
    def player_detail(player_id):
        player_resp = api_get(f"/players/{player_id}")
        player = player_resp["data"] if player_resp and "data" in player_resp else None

        team = None
        if player and "team" in player and player["team"]:
            team_id = player["team"]["id"]
            team_resp = api_get(f"/teams/{team_id}")
            team = team_resp["data"] if team_resp and "data" in team_resp else None

        return render_template("player_detail.html", player=player, team=team)

    @app.get("/teams")
    @login_required
    def teams():
        teams = api_get("/teams")
        if not teams:
            abort(502)
        return render_template("teams.html", teams=teams.get("data", []))

    @app.get("/teams/<int:team_id>")
    @login_required
    def team_detail(team_id):
        team_resp = api_get(f"/teams/{team_id}")
        if not team_resp or "data" not in team_resp:
            abort(404)
        team = team_resp["data"]

        players = api_get("/players", params={"per_page": 100, "team_ids[]": team_id})
        team_players = players.get("data", []) if players else []

        return render_template("team_detail.html", team=team, players=team_players)

    @app.get("/games")
    @login_required
    def games():
        cursor = int(request.args.get("cursor", 0))   
        per_page = 24

        resp = api_get(f"/games?cursor={cursor}&per_page={per_page}")
        if not resp or "data" not in resp:
            games = []
            meta = {"next_cursor": None}
        else:
            games = resp["data"]
            meta = resp.get("meta", {"next_cursor": None})

        print("=== META GAMES ===")
        print(meta)

        return render_template("games.html", games=games, meta=meta, cursor=cursor, per_page=per_page)


    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))