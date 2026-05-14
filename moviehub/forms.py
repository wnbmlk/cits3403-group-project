from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length, ValidationError

from .models import User


def validate_password_strength(password):
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


class SignupForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(message="Username is required"), Length(min=3, max=80, message="Username must be between 3 and 80 characters")],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required"), Length(min=8, max=128, message="Password must be at least 8 characters long")],
    )

    def validate_username(self, field):
        existing = User.query.filter_by(username=field.data).first()
        if existing:
            raise ValidationError("User already exists")

    def validate_password(self, field):
        is_valid, message = validate_password_strength(field.data or "")
        if not is_valid:
            raise ValidationError(message)


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(message="Username is required")],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required")],
    )