
import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-only-change-this-secret"
)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "codesphere.db"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


init_db()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Mag-login muna para ma-access ang feature na ito.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


CONTENT = {
    "learning": {
        "title": "Learning Hub",
        "intro": "Matuto ng programming at IT skills sa sarili mong pace.",
        "items": [
            ("🐍", "Python Fundamentals", "Variables, loops, functions, at beginner exercises.", "https://docs.python.org/3/tutorial/"),
            ("🌐", "HTML at CSS", "Gumawa ng responsive websites at modern layouts.", "https://developer.mozilla.org/en-US/docs/Learn_web_development"),
            ("⚡", "JavaScript", "Matuto ng interactive web programming.", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
            ("🗄️", "Database Basics", "Alamin ang tables, queries, at relational databases.", "https://www.postgresql.org/docs/")
        ]
    },
    "projects": {
        "title": "Project Showcase",
        "intro": "Mga project idea na puwede mong buuin at idagdag sa portfolio.",
        "items": [
            ("🎓", "Student Management System", "Mag-record ng students, subjects, at grades.", "https://github.com/topics/student-management-system"),
            ("🛒", "Inventory System", "Mag-track ng products, stock, at transactions.", "https://github.com/topics/inventory-management"),
            ("🌦️", "Weather Dashboard", "Gumawa ng dashboard na gumagamit ng weather API.", "https://github.com/topics/weather-app"),
            ("🔐", "Login System", "Mag-aral ng authentication at password security.", "https://flask.palletsprojects.com/")
        ]
    },
    "tools": {
        "title": "Developer Tools",
        "intro": "Mga kapaki-pakinabang na tools mula sa kanilang official websites.",
        "items": [
            ("💻", "Visual Studio Code", "Code editor para sa web development at Python.", "https://code.visualstudio.com/"),
            ("🐍", "Python", "Programming language para sa web, automation, at data.", "https://www.python.org/downloads/"),
            ("🔧", "Git", "Version control para masubaybayan ang code changes.", "https://git-scm.com/downloads"),
            ("🐙", "GitHub", "I-host ang repositories at makipagtulungan sa projects.", "https://github.com/"),
            ("🧪", "Postman", "Subukan at i-debug ang APIs.", "https://www.postman.com/"),
            ("🗃️", "DB Browser for SQLite", "Tingnan at pamahalaan ang SQLite databases.", "https://sqlitebrowser.org/")
        ]
    },
    "careers": {
        "title": "IT Career Roadmap",
        "intro": "Pumili ng career path at tukuyin ang mga skill na dapat pag-aralan.",
        "items": [
            ("🌐", "Web Developer", "HTML, CSS, JavaScript, Python, Flask, at databases.", "https://developer.mozilla.org/"),
            ("🛡️", "Cybersecurity Analyst", "Networking, Linux, security fundamentals, at ethical practice.", "https://www.cisa.gov/cybersecurity"),
            ("📊", "Data Analyst", "Excel, SQL, Python, statistics, at visualization.", "https://pandas.pydata.org/docs/"),
            ("☁️", "Cloud Engineer", "Networking, Linux, cloud infrastructure, at deployment.", "https://aws.amazon.com/getting-started/"),
            ("🧑‍💻", "Software Engineer", "Programming, algorithms, testing, Git, at system design.", "https://github.com/resources/articles")
        ]
    },
    "community": {
        "title": "Tech Community",
        "intro": "Mga discussion prompt para sa IT students at professionals.",
        "items": [
            ("💬", "Introduce Yourself", "Ano ang pinag-aaralan mo at anong tech skill ang gusto mong matutunan?", "https://github.com/orgs/community/discussions"),
            ("🧠", "Programming Tips", "Ibahagi ang coding tips at mga natutuhan mong lessons.", "https://stackoverflow.com/questions"),
            ("🚀", "Project Feedback", "Ipakita ang iyong project sa GitHub at humingi ng feedback.", "https://github.com/explore"),
            ("🤝", "Collaboration", "Maghanap ng open-source projects na puwedeng salihan.", "https://goodfirstissue.dev/")
        ]
    },
    "about": {
        "title": "About CodeSphere",
        "intro": "Learn. Build. Connect. Innovate.",
        "items": [
            ("🎯", "Our Mission", "Gawing mas accessible ang IT learning at career development."),
            ("🎓", "For Students", "Makahanap ng learning resources, project ideas, at practice."),
            ("💼", "For Professionals", "Mag-discover ng tools at patuloy na i-develop ang technical skills."),
            ("🌱", "Our Vision", "Bumuo ng supportive space para sa mga taong gustong lumago sa technology.")
        ]
    }
}


@app.route("/")
def home():
    featured = [
        ("📚", "Learning Hub", "Matuto ng programming at web development.", url_for("section", name="learning")),
        ("🧩", "Project Showcase", "Maghanap ng project ideas para sa portfolio.", url_for("section", name="projects")),
        ("🛠️", "Developer Tools", "Discover tools at official downloads.", url_for("section", name="tools")),
        ("🧭", "Career Roadmap", "Planuhin ang susunod mong hakbang sa IT.", url_for("section", name="careers"))
    ]
    return render_template("page.html", page={
        "title": "Build Your Future in Tech",
        "intro": "Welcome to CodeSphere — your hub for learning, building projects, and growing your IT career.",
        "items": featured
    }, home=True)


@app.route("/<name>")
def section(name):
    if name not in CONTENT:
        return render_template("page.html", page={
            "title": "Page Not Found",
            "intro": "Hindi namin makita ang page na hinahanap mo.",
            "items": []
        }), 404
    return render_template("page.html", page=CONTENT[name], home=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("Punan ang lahat ng fields.", "error")
        elif len(password) < 8:
            flash("Dapat ay hindi bababa sa 8 characters ang password.", "error")
        else:
            db = get_db()
            try:
                cursor = db.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                    (username, email, generate_password_hash(password))
                )
                db.commit()
                session.clear()
                session["user_id"] = cursor.lastrowid
                session["username"] = username
                flash("Matagumpay ang registration! Welcome sa CodeSphere.", "success")
                return redirect(url_for("home"))
            except sqlite3.IntegrityError:
                flash("May account na gamit ang email na iyan.", "error")

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Matagumpay kang naka-login.", "success")
            return redirect(url_for("home"))

        flash("Mali ang email o password.", "error")

    return render_template("auth.html", mode="login")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Nag-logout ka na.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    return render_template("page.html", page={
        "title": "My Profile",
        "intro": f"Welcome, {session.get('username')}! Naka-login ka sa CodeSphere.",
        "items": [
            ("👤", "Account", "May sarili ka nang CodeSphere account."),
            ("📚", "Learning", "Bisitahin ang Learning Hub para simulan ang iyong learning journey."),
            ("🚀", "Next Step", "Buuin ang iyong unang project at idagdag sa portfolio.")
        ]
    }, home=False)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Punan ang lahat ng fields.", "error")
        elif len(message) > 5000:
            flash("Masyadong mahaba ang message (maximum 5000 characters).", "error")
        else:
            get_db().execute(
                "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message)
            )
            get_db().commit()
            flash("Salamat! Na-save ang iyong feedback.", "success")
            return redirect(url_for("contact"))

    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
