import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate


def load_env_file(env_path):
    if not os.path.exists(env_path):
        return

    with open(env_path, encoding="utf-8") as env_file:
        for line in env_file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


def get_database_uri():
    database_uri = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if database_uri and database_uri.startswith("postgres://"):
        return database_uri.replace("postgres://", "postgresql://", 1)

    if database_uri and database_uri.startswith("sqlite:///"):
        sqlite_path = database_uri.replace("sqlite:///", "", 1)
        if not os.path.isabs(sqlite_path):
            sqlite_path = os.path.join(os.path.dirname(__file__), sqlite_path)
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        return f"sqlite:///{sqlite_path}"

    if database_uri:
        return database_uri

    database_path = os.path.join(os.path.dirname(__file__), "instance", "moviehub.db")
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    return f"sqlite:///{database_path}"


app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    genre = db.Column(db.String(80), nullable=True)
    rating = db.Column(db.Float, nullable=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)


class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "genre": self.genre,
            "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id
        }


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    flash("Please log in to access the diary and profile pages.", "warning")
    return redirect(url_for("login"))


def validate_password(password):
    """
    Validate password strength.
    Returns a tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    special_chars = "!@#$%^&*()-_=+[]{};:'\",.< >?/\\|`~"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character (!@#$%^&* etc.)"

    return True, None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/api/password-strength", methods=["POST"])
def check_password_strength():
    """API endpoint for real-time password strength checking"""
    data = request.get_json()
    password = data.get("password", "")

    is_valid, error_msg = validate_password(password)

    strength_score = 0
    if len(password) >= 8:
        strength_score += 1
    if any(c.isupper() for c in password):
        strength_score += 1
    if any(c.islower() for c in password):
        strength_score += 1
    if any(c.isdigit() for c in password):
        strength_score += 1

    special_chars = "!@#$%^&*()-_=+[]{};:'\",.< >?/\\|`~"
    if any(c in special_chars for c in password):
        strength_score += 1

    return {
        "valid": is_valid,
        "score": strength_score,
        "error": error_msg,
        "requirements": {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "number": any(c.isdigit() for c in password),
            "special": any(c in special_chars for c in password),
        }
    }

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password required", "danger")
            return redirect(url_for("signup"))

        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, "danger")
            return redirect(url_for("signup"))

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("User already exists", "warning")
            return redirect(url_for("signup"))

        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("profile"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = None
        if username:
            user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for("profile"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/diary")
@login_required
def diary():
    return render_template("diary.html")


@app.route("/api/diary/entries", methods=["GET"])
@login_required
def get_diary_entries():
    """Get all diary entries for the current user"""
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.date.desc()).all()
    return {"entries": [entry.to_dict() for entry in entries]}


@app.route("/api/diary/entries", methods=["POST"])
@login_required
def create_diary_entry():
    """Create a new diary entry for the current user"""
    data = request.get_json()
    
    if not data or "title" not in data or "status" not in data or "date" not in data:
        return {"error": "Missing required fields"}, 400
    
    try:
        date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return {"error": "Invalid date format"}, 400
    
    entry = DiaryEntry(
        title=data["title"],
        status=data["status"],
        genre=data.get("genre"),
        date=date,
        user_id=current_user.id
    )
    
    db.session.add(entry)
    db.session.commit()
    
    return entry.to_dict(), 201


@app.route("/api/diary/entries/<int:entry_id>", methods=["PUT"])
@login_required
def update_diary_entry(entry_id):
    """Update a diary entry"""
    entry = DiaryEntry.query.get(entry_id)
    
    if not entry:
        return {"error": "Entry not found"}, 404
    
    if entry.user_id != current_user.id:
        return {"error": "Forbidden"}, 403
    
    data = request.get_json()
    
    if "title" in data:
        entry.title = data["title"]
    if "status" in data:
        entry.status = data["status"]
    if "genre" in data:
        entry.genre = data["genre"]
    if "date" in data:
        try:
            entry.date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return {"error": "Invalid date format"}, 400
    
    db.session.commit()
    return entry.to_dict()


@app.route("/api/diary/entries/<int:entry_id>", methods=["DELETE"])
@login_required
def delete_diary_entry(entry_id):
    """Delete a diary entry"""
    entry = DiaryEntry.query.get(entry_id)
    
    if not entry:
        return {"error": "Entry not found"}, 404
    
    if entry.user_id != current_user.id:
        return {"error": "Forbidden"}, 403
    
    db.session.delete(entry)
    db.session.commit()
    
    return {"success": True}


if __name__ == "__main__":
    os.makedirs(app.instance_path, exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)