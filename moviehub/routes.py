from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .models import DiaryEntry, Movie, User


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


def home():
    return render_template("index.html")


def about():
    return render_template("about.html")


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
        },
    }


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


@login_required
def profile():
    return render_template("profile.html", user=current_user)


@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_required
def diary():
    movie_catalog = [movie.to_dict() for movie in Movie.query.order_by(Movie.title.asc()).all()]
    return render_template("diary.html", movie_catalog=movie_catalog)


@login_required
def get_diary_entries():
    """Get all diary entries for the current user"""
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.date.desc()).all()
    return {"entries": [entry.to_dict() for entry in entries]}


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
        poster_path=data.get("poster_path"),
        date=date,
        user_id=current_user.id,
    )

    db.session.add(entry)
    db.session.commit()

    return entry.to_dict(), 201


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
    if "poster_path" in data:
        entry.poster_path = data["poster_path"]
    if "date" in data:
        try:
            entry.date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return {"error": "Invalid date format"}, 400

    db.session.commit()
    return entry.to_dict()


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