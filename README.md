# Movie Diary Project

This repository contains a CITS3403 group project for a simple movie diary web application.

## Team Members

| UWA ID | Name | GitHub |
| --- | --- | --- |
| 24280931 | Abbas Fadaee | Abbas-f |
| 23993402 | Chris Chandra | ChrstphrC |
| 21703254 | Samuel Bengtsson | AprioriCaffeination |
| 24247407 | Wenbo Zhong | wnbmlk |

## Project Idea

The application lets users log in, save the movies and series they have watched, keep a watchlist of titles they want to see, and optionally mark favourites on a public profile. Other users can search for a profile and view selected public activity, which satisfies the requirement to view data from other users.

## Planned Pages

- Home / landing page
- Sign up page
- Login page
- Dashboard page
- My diary page
- Search users page
- Public profile page
- Add / edit movie entry page
- Logout action

## Core Features

- Client-server architecture with Flask
- Login and logout
- Persistent user data between sessions
- Public user profiles with watched, watching, and want-to-watch tabs
- Optional favourites section for movies or series

## Technologies

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **CSS Framework:** Bootstrap
- **Database:** SQLite (via SQLAlchemy ORM)

## Environment Variables

Create a local `.env` file based on `.env.example` and keep it out of Git.

- `SECRET_KEY`: Flask session secret, used for signed cookies and flash/session security. Defaults to `dev-secret-key-change-me`.
- `DATABASE_URL`: Database connection string. For local development, defaults to `sqlite:///instance/moviehub.db`. For production or shared development, set this to a PostgreSQL URL.

**Security:** Passwords are hashed using Werkzeug's `generate_password_hash` before storage. The secret key is never used for password storage or recovery.

## Run Locally

1. Activate the virtual environment.

```bash
source .venv/bin/activate
```

2. Set the Flask app entrypoint to the new launcher.

```bash
export FLASK_APP=run.py
```

3. Run the development server.

```bash
./.venv/bin/flask run
```

If you need to create or update the local database schema, run migrations with the same entrypoint:

```bash
export FLASK_APP=run.py && ./.venv/bin/flask db migrate -m "describe changes" && ./.venv/bin/flask db upgrade
```

## Post-Setup: Seed Demo Data

After running migrations for the first time (or after deleting the database), seed the app with demo movies and diary entries:

```bash
./.venv/bin/python seed_demo_data.py
```

This creates a `demo` user with 100 movies and 50 anime diary entries, plus SVG poster placeholders. The seeder is idempotent: running it again will not duplicate entries.

**Important:** Ensure your `DATABASE_URL` environment variable (if set) matches the one used during `flask db upgrade`. If they differ, the seeder will populate a different database than the app reads.

Example (for a specific database file):
```bash
export DATABASE_URL=sqlite:///instance/moviehub.db
./.venv/bin/flask db upgrade
./.venv/bin/python seed_demo_data.py
./.venv/bin/flask run
```

## Testing

### Unit Tests

Run the pytest test suite:

```bash
source .venv/bin/activate
pytest tests/test_auth.py tests/test_diary.py -v
```

This runs 11 unit tests covering:
- User signup (valid/invalid/duplicate credentials)
- User login (valid/invalid credentials)
- Password strength validation
- Diary entry CRUD operations
- Access control and permissions

### Selenium Acceptance Tests

To run browser-based acceptance tests:

```bash
source .venv/bin/activate
# Ensure Flask app is running on port 5001
pytest tests/test_selenium_acceptance.py -v
```

**Prerequisites:**
- Chrome/Chromium browser installed
- ChromeDriver installed and in PATH (or use `webdriver-manager`)
- Flask app must be running: `flask run --port 5001` (in another terminal)

Selenium tests verify:
- Complete user signup flow
- Login and authentication
- Diary entry creation, editing, and deletion
- Profile page display
- User search functionality

### Code Quality

- All route functions include docstrings explaining purpose, parameters, and return values
- XSS prevention: User-generated content escaped in templates with `|escape` filter
- CSRF protection enabled on all forms and AJAX requests
- Password validation enforced: 8+ chars with uppercase, lowercase, digits, special chars

