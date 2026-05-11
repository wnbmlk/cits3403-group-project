from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from .extensions import db
from .models import DiaryEntry, Movie, User, _display_poster_path


ALLOWED_STATUS_MAP = {
    "watched": "Watched",
    "watchlist": "Watchlist",
    "favourite": "Favourite",
    "favorite": "Favourite",
    "watching": "Watching",
}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024


def _slugify(value):
    normalized = "".join(character.lower() if character.isalnum() else "-" for character in value)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")


def _normalize_statuses(values):
    if isinstance(values, str):
        raw_values = [chunk.strip() for chunk in values.split(",")]
    else:
        raw_values = [str(value).strip() for value in (values or [])]

    normalized = []
    for value in raw_values:
        key = value.lower()
        if not key:
            continue
        mapped = ALLOWED_STATUS_MAP.get(key)
        if mapped and mapped not in normalized:
            normalized.append(mapped)

    return normalized


def _validate_title(value):
    title = (value or "").strip()
    if not title:
        return None, "Title is required"
    if len(title) > 200:
        return None, "Title must be 200 characters or less"
    return title, None


def _validate_genre(value):
    genre = (value or "").strip()
    if len(genre) > 100:
        return None, "Genre must be 100 characters or less"
    return genre or None, None


def _parse_date_or_today(value):
    if not value:
        now = datetime.utcnow()
        return now.replace(hour=0, minute=0, second=0, microsecond=0), None

    try:
        date = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return date, None
    except (ValueError, AttributeError):
        return None, "Invalid date format"


def _save_uploaded_poster(file_storage):
    if not file_storage:
        return None, None

    filename = secure_filename(file_storage.filename or "")
    if not filename:
        return None, None

    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Unsupported image type"

    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_UPLOAD_SIZE:
        return None, "Image must be 5MB or smaller"

    uploads_dir = Path(__file__).resolve().parent.parent / "static" / "images" / "posters" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    safe_name = f"{uuid4().hex}{extension}"
    target = uploads_dir / safe_name
    file_storage.save(target)

    return f"/static/images/posters/uploads/{safe_name}", None


def _upsert_movie_catalog_entry(title, genre=None, poster_path=None, media_type=None):
    resolved_poster_path = _resolve_tmdb_poster_path(title, poster_path)
    existing_movie = Movie.query.filter(db.func.lower(Movie.title) == title.lower()).first()
    if existing_movie:
        if genre and not existing_movie.genre:
            existing_movie.genre = genre
        if resolved_poster_path and (not existing_movie.poster_path or existing_movie.poster_path.endswith(".svg")):
            existing_movie.poster_path = resolved_poster_path
        if media_type and not existing_movie.media_type:
            existing_movie.media_type = media_type
        return

    db.session.add(
        Movie(
            title=title,
            media_type=media_type,
            genre=genre,
            poster_path=resolved_poster_path,
        )
    )


def _resolve_tmdb_poster_path(title, fallback_path=None):
    slug = _slugify(title)
    tmdb_path = f"/static/images/posters/tmdb/{slug}.jpg"
    tmdb_file = Path(current_app.static_folder) / "images" / "posters" / "tmdb" / f"{slug}.jpg"

    if tmdb_file.exists():
        return tmdb_path

    return fallback_path


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
    if current_user.is_authenticated:
        entries = [
            {
                "title": entry.title,
                "status": entry.status,
                "media_type": entry.media_type,
                "genre": entry.genre,
                "poster_path": _display_poster_path(entry.title, entry.poster_path),
                "date": entry.date,
            }
            for entry in DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.date.desc()).limit(9).all()
        ]
    else:
        entries = [
            {
                "title": entry.title,
                "status": entry.status,
                "media_type": entry.media_type,
                "genre": entry.genre,
                "poster_path": _display_poster_path(entry.title, entry.poster_path),
                "date": entry.date,
            }
            for entry in DiaryEntry.query.filter(DiaryEntry.poster_path.isnot(None)).order_by(db.func.random()).limit(9).all()
        ]
    return render_template("index.html", entries=entries)


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
        session["boot_id"] = current_app.config.get("SESSION_BOOT_ID")
        return redirect(url_for("profile"))

    return render_template("signup.html")


def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = None
        if username:
            user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session.permanent = False
            login_user(user, remember=False)
            session["boot_id"] = current_app.config.get("SESSION_BOOT_ID")
            return redirect(url_for("profile"))

        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


def _entry_status_tokens(entry):
    return set(_normalize_statuses(entry.status))


def _entry_has_status(entry, status_name):
    return status_name in _entry_status_tokens(entry)


def _format_profile_date(entry_date):
    if not entry_date:
        return "Unknown date"

    return entry_date.strftime("%d %b %Y")


def _build_profile_summary(user_id):
    entries = DiaryEntry.query.filter_by(user_id=user_id).order_by(DiaryEntry.date.desc()).all()

    watched_entries = []
    watching_entries = []
    watchlist_entries = []
    favourite_entries = []

    for entry in entries:
        item = {
            "id": entry.id,
            "title": entry.title,
            "media_type": entry.media_type,
            "genre": entry.genre,
            "status": entry.status,
            "poster_path": _display_poster_path(entry.title, entry.poster_path),
            "date_label": _format_profile_date(entry.date),
            "date_range_label": (
                f"{_format_profile_date(entry.date)} - {_format_profile_date(entry.date_watched_end)}"
                if entry.date_watched_end
                else _format_profile_date(entry.date)
            ),
        }

        if _entry_has_status(entry, "Watched"):
            watched_entries.append(item)
        if _entry_has_status(entry, "Watching"):
            watching_entries.append(item)
        if _entry_has_status(entry, "Watchlist"):
            watchlist_entries.append(item)
        if _entry_has_status(entry, "Favourite"):
            favourite_entries.append(item)

    return {
        "watched": watched_entries[:5],
        "watching": watching_entries[:5],
        "watchlist": watchlist_entries[:5],
        "favourites": favourite_entries[:10],
        "counts": {
            "watched": len(watched_entries),
            "watching": len(watching_entries),
            "watchlist": len(watchlist_entries),
            "favourites": len(favourite_entries),
        },
    }


def _find_user_by_username(username):
    normalized_username = (username or "").strip()
    if not normalized_username:
        return None

    return User.query.filter(db.func.lower(User.username) == normalized_username.lower()).first()


@login_required
def profile():
    profile_summary = _build_profile_summary(current_user.id)
    return render_template(
        "profile.html",
        profile_user=current_user,
        profile_summary=profile_summary,
        is_public=False,
    )


@login_required
def user_search():
    query = (request.args.get("q") or "").strip()
    searched_user = _find_user_by_username(query) if query else None
    return render_template("users_search.html", query=query, searched_user=searched_user)


@login_required
def public_profile(username):
    profile_user = _find_user_by_username(username)
    if not profile_user:
        return render_template("users_search.html", query=username, searched_user=None, search_error="User not found"), 404

    profile_summary = _build_profile_summary(profile_user.id)
    return render_template(
        "profile.html",
        profile_user=profile_user,
        profile_summary=profile_summary,
        is_public=True,
    )


@login_required
def logout():
    logout_user()
    session.clear()
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

    title, title_error = _validate_title(data.get("title"))
    if title_error:
        return {"error": title_error}, 400

    statuses = _normalize_statuses(data.get("status"))
    if not statuses:
        return {"error": "Please provide at least one valid status"}, 400

    genre, genre_error = _validate_genre(data.get("genre"))
    if genre_error:
        return {"error": genre_error}, 400

    date, date_error = _parse_date_or_today(data.get("date"))
    if date_error:
        return {"error": date_error}, 400

    date_watched_end = None
    if data.get("date_watched_end"):
        date_watched_end, date_error = _parse_date_or_today(data.get("date_watched_end"))
        if date_error:
            return {"error": date_error}, 400

    poster_path = _resolve_tmdb_poster_path(title, (data.get("poster_path") or "").strip() or None)

    # Try to find matching Movie to extract media_type
    matching_movie = Movie.query.filter(db.func.lower(Movie.title) == title.lower()).first()
    media_type = matching_movie.media_type if matching_movie else None

    entry = DiaryEntry(
        title=title,
        status=", ".join(statuses),
        media_type=media_type,
        genre=genre,
        poster_path=poster_path,
        date=date,
        date_watched_end=date_watched_end,
        user_id=current_user.id,
    )

    db.session.add(entry)
    _upsert_movie_catalog_entry(title=title, genre=genre, poster_path=poster_path, media_type=media_type)
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
        title, title_error = _validate_title(data.get("title"))
        if title_error:
            return {"error": title_error}, 400
        entry.title = title
    if "status" in data:
        statuses = _normalize_statuses(data.get("status"))
        if not statuses:
            return {"error": "Please provide at least one valid status"}, 400
        entry.status = ", ".join(statuses)
    if "genre" in data:
        genre, genre_error = _validate_genre(data.get("genre"))
        if genre_error:
            return {"error": genre_error}, 400
        entry.genre = genre
    if "poster_path" in data:
        entry.poster_path = _resolve_tmdb_poster_path(entry.title, (data.get("poster_path") or "").strip() or None)
    if "date" in data:
        date, date_error = _parse_date_or_today(data.get("date"))
        if date_error:
            return {"error": date_error}, 400
        entry.date = date
    if "date_watched_end" in data:
        if data.get("date_watched_end"):
            date_watched_end, date_error = _parse_date_or_today(data.get("date_watched_end"))
            if date_error:
                return {"error": date_error}, 400
            entry.date_watched_end = date_watched_end
        else:
            entry.date_watched_end = None

    _upsert_movie_catalog_entry(title=entry.title, genre=entry.genre, poster_path=entry.poster_path)
    db.session.commit()
    return entry.to_dict()


@login_required
def create_manual_diary_entry():
    title, title_error = _validate_title(request.form.get("title"))
    if title_error:
        return {"error": title_error}, 400

    genre, genre_error = _validate_genre(request.form.get("genre"))
    if genre_error:
        return {"error": genre_error}, 400

    statuses = _normalize_statuses(request.form.getlist("statuses"))
    if not statuses:
        statuses = _normalize_statuses(request.form.get("status"))
    if not statuses:
        return {"error": "Please choose at least one valid status"}, 400

    date, date_error = _parse_date_or_today(request.form.get("date"))
    if date_error:
        return {"error": date_error}, 400

    date_watched_end = None
    if request.form.get("date_watched_end"):
        date_watched_end, date_error = _parse_date_or_today(request.form.get("date_watched_end"))
        if date_error:
            return {"error": date_error}, 400

    poster_path, upload_error = _save_uploaded_poster(request.files.get("photo"))
    if upload_error:
        return {"error": upload_error}, 400

    # Try to find matching Movie to extract media_type
    matching_movie = Movie.query.filter(db.func.lower(Movie.title) == title.lower()).first()
    media_type = matching_movie.media_type if matching_movie else None

    entry = DiaryEntry(
        title=title,
        status=", ".join(statuses),
        media_type=media_type,
        genre=genre,
        poster_path=poster_path or _resolve_tmdb_poster_path(title),
        date=date,
        date_watched_end=date_watched_end,
        user_id=current_user.id,
    )

    db.session.add(entry)
    _upsert_movie_catalog_entry(title=title, genre=genre, poster_path=poster_path, media_type=media_type)
    db.session.commit()

    return entry.to_dict(), 201


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