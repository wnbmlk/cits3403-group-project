from datetime import datetime
from pathlib import Path

from flask import current_app
from flask_login import UserMixin

from .extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


def _display_poster_path(title, poster_path):
    if not poster_path:
        return poster_path

    if "/uploads/" in poster_path:
        return poster_path

    if not title:
        return poster_path

    slug = "".join(character.lower() if character.isalnum() else "-" for character in title)
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-")

    tmdb_path = f"/static/images/posters/tmdb/{slug}.jpg"
    tmdb_file = Path(current_app.static_folder) / "images" / "posters" / "tmdb" / f"{slug}.jpg"
    if tmdb_file.exists():
        return tmdb_path

    return poster_path


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    media_type = db.Column(db.String(50), nullable=True)
    genre = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    poster_path = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "media_type": self.media_type,
            "genre": self.genre,
            "status": self.status,
            "poster_path": _display_poster_path(self.title, self.poster_path),
            "rating": self.rating,
        }


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
    media_type = db.Column(db.String(50), nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    poster_path = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    date_watched_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "media_type": self.media_type,
            "genre": self.genre,
            "poster_path": _display_poster_path(self.title, self.poster_path),
            "date": self.date.isoformat(),
            "date_watched_end": self.date_watched_end.isoformat() if self.date_watched_end else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
        }