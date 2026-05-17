from pathlib import Path
from uuid import uuid4
from sqlalchemy import inspect, text

from flask import Flask, flash, redirect, session, url_for
from flask_login import current_user, logout_user

from . import routes
from .config import Config
from .extensions import csrf, db, login_manager, migrate
from .models import User


def create_app(config_object=Config):
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config.from_object(config_object)
    app.config["SESSION_BOOT_ID"] = uuid4().hex

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    @login_manager.unauthorized_handler
    def unauthorized():
        flash("Please log in to access the diary and profile pages.", "warning")
        return redirect(url_for("login"))

    @app.before_request
    def invalidate_stale_sessions():
        if not current_user.is_authenticated:
            return
        session_boot_id = session.get("boot_id")
        current_boot_id = app.config.get("SESSION_BOOT_ID")
        if session_boot_id and session_boot_id == current_boot_id:
            return
        logout_user()
        session.clear()
        flash("Your session expired when the app restarted. Please log in again.", "warning")
        return redirect(url_for("login"))

    with app.app_context():
        _ensure_diary_entry_poster_column()
        _ensure_diary_entry_date_watched_end_column()
        _ensure_movie_columns()

    app.add_url_rule("/", endpoint="home", view_func=routes.home)
    app.add_url_rule("/about", endpoint="about", view_func=routes.about)
    app.add_url_rule("/api/password-strength", endpoint="check_password_strength", view_func=routes.check_password_strength, methods=["POST"])
    app.add_url_rule("/signup", endpoint="signup", view_func=routes.signup, methods=["GET", "POST"])
    app.add_url_rule("/login", endpoint="login", view_func=routes.login, methods=["GET", "POST"])
    app.add_url_rule("/profile", endpoint="profile", view_func=routes.profile)
    app.add_url_rule("/users", endpoint="user_search", view_func=routes.user_search, methods=["GET"])
    app.add_url_rule("/users/<username>", endpoint="public_profile", view_func=routes.public_profile, methods=["GET"])
    app.add_url_rule("/logout", endpoint="logout", view_func=routes.logout)
    app.add_url_rule("/diary", endpoint="diary", view_func=routes.diary)
    app.add_url_rule("/api/diary/entries", endpoint="get_diary_entries", view_func=routes.get_diary_entries, methods=["GET"])
    app.add_url_rule("/api/diary/entries", endpoint="create_diary_entry", view_func=routes.create_diary_entry, methods=["POST"])
    app.add_url_rule("/api/diary/manual-entry", endpoint="create_manual_diary_entry", view_func=routes.create_manual_diary_entry, methods=["POST"])
    app.add_url_rule("/api/diary/entries/<int:entry_id>", endpoint="update_diary_entry", view_func=routes.update_diary_entry, methods=["PUT"])
    app.add_url_rule("/api/diary/entries/<int:entry_id>", endpoint="delete_diary_entry", view_func=routes.delete_diary_entry, methods=["DELETE"])
    # NEW: diary stats endpoint
    app.add_url_rule("/api/diary/stats", endpoint="get_diary_stats", view_func=routes.get_diary_stats, methods=["GET"])
    app.add_url_rule("/movie/<int:movie_id>", endpoint="movie_detail", view_func=routes.movie_detail)

    return app


def _ensure_diary_entry_poster_column():
    engine = db.engine
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    if "diary_entry" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("diary_entry")}
    if "poster_path" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE diary_entry ADD COLUMN poster_path VARCHAR(255)"))


def _ensure_diary_entry_date_watched_end_column():
    engine = db.engine
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    if "diary_entry" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("diary_entry")}
    if "date_watched_end" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE diary_entry ADD COLUMN date_watched_end DATETIME"))


def _ensure_movie_columns():
    engine = db.engine
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    if "movie" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("movie")}
    statements = []
    if "media_type" not in columns:
        statements.append("ALTER TABLE movie ADD COLUMN media_type VARCHAR(50)")
    if "status" not in columns:
        statements.append("ALTER TABLE movie ADD COLUMN status VARCHAR(50)")
    if "poster_path" not in columns:
        statements.append("ALTER TABLE movie ADD COLUMN poster_path VARCHAR(255)")
    if "rating" not in columns:
        statements.append("ALTER TABLE movie ADD COLUMN rating FLOAT")
    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))