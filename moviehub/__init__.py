from pathlib import Path

from flask import Flask, flash, redirect, url_for

from . import routes
from .config import Config
from .extensions import db, login_manager, migrate
from .models import User


def create_app(config_object=Config):
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
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

    app.add_url_rule("/", endpoint="home", view_func=routes.home)
    app.add_url_rule("/about", endpoint="about", view_func=routes.about)
    app.add_url_rule("/api/password-strength", endpoint="check_password_strength", view_func=routes.check_password_strength, methods=["POST"])
    app.add_url_rule("/signup", endpoint="signup", view_func=routes.signup, methods=["GET", "POST"])
    app.add_url_rule("/login", endpoint="login", view_func=routes.login, methods=["GET", "POST"])
    app.add_url_rule("/profile", endpoint="profile", view_func=routes.profile)
    app.add_url_rule("/logout", endpoint="logout", view_func=routes.logout)
    app.add_url_rule("/diary", endpoint="diary", view_func=routes.diary)
    app.add_url_rule("/api/diary/entries", endpoint="get_diary_entries", view_func=routes.get_diary_entries, methods=["GET"])
    app.add_url_rule("/api/diary/entries", endpoint="create_diary_entry", view_func=routes.create_diary_entry, methods=["POST"])
    app.add_url_rule("/api/diary/entries/<int:entry_id>", endpoint="update_diary_entry", view_func=routes.update_diary_entry, methods=["PUT"])
    app.add_url_rule("/api/diary/entries/<int:entry_id>", endpoint="delete_diary_entry", view_func=routes.delete_diary_entry, methods=["DELETE"])
    app.add_url_rule("/movie/<int:movie_id>", "movie_detail", routes.movie_detail)

    return app