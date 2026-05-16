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

### Prerequisites

- Python 3.10+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- Chrome/Chromium (for Selenium tests)

### Quick Start

1. **Clone and setup virtual environment:**
```bash
git clone https://github.com/your-username/cits3403-group-project.git
cd cits3403-group-project
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file:**
```bash
cp .env.example .env
# Edit .env and add: SECRET_KEY=your-secret-key, DATABASE_URL=sqlite:///instance/moviehub.db
```

4. **Initialize database and seed demo data:**
```bash
flask db upgrade
python3 seed_demo_data.py
```

5. **Run the application:**
```bash
python3 app.py
```

Visit **http://localhost:5000** | Demo credentials: `demo` / `demo`

### Database Commands

Reset database:
```bash
rm instance/moviehub.db
flask db upgrade
python3 seed_demo_data.py
```

Create migration after model changes:
```bash
flask db migrate -m "describe changes"
flask db upgrade
```

## Testing

### Run All Tests

```bash
source .venv/bin/activate
pytest tests/unit_tests.py tests/selenium_tests.py -v
```

Expected: **24 tests passing** in ~35 seconds

### Unit Tests Only (Faster, no browser)

```bash
pytest tests/unit_tests.py -v
```

**17 tests:** User signup/login, password validation, diary CRUD, access control

### Selenium Tests (End-to-end workflows with browser)

```bash
pytest tests/selenium_tests.py -v
```

**7 tests:** Signup → login → create diary → search users → verify all pages load

### Code Quality

- All route functions include docstrings explaining purpose, parameters, and return values
- XSS prevention: User-generated content escaped in templates with `|escape` filter
- CSRF protection enabled on all forms and AJAX requests
- Password validation enforced: 8+ chars with uppercase, lowercase, digits, special chars

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

**Solution:** Virtual environment not activated or dependencies not installed.

```bash
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### "Address already in use" (Port 5000)

**Solution:** Another app is using port 5000, or Flask server didn't shut down cleanly.

```bash
# Kill the process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows (then taskkill /PID <PID> /F)

# Or specify a different port
flask run --port 5001
```

### Selenium tests fail with "ChromeDriver error"

**Solution:** `webdriver-manager` should handle this automatically. If issues persist:

```bash
pip install --upgrade webdriver-manager
pytest tests/selenium_tests.py -v  # Should auto-download ChromeDriver
```

### "No such file or directory: 'instance/moviehub.db'"

**Solution:** Database file doesn't exist. Initialize it:

```bash
export FLASK_APP=run.py
flask db upgrade
python seed_demo_data.py  # Optional
```

### "RuntimeError: Working outside of request context"

**Solution:** Make sure to activate virtual environment and use `flask run` instead of `python run.py`:

```bash
source .venv/bin/activate
export FLASK_APP=run.py
flask run
```

### Tests pass individually but fail together

**Solution:** Database state or port conflict. This is normal - tests clean up after themselves:

```bash
# Run tests with more verbosity to diagnose
pytest tests/ -v --tb=short

# Or run individually
pytest tests/unit_tests.py -v
pytest tests/selenium_tests.py -v
```

## Project Structure

```
cits3403-group-project/
├── moviehub/                    # Main Flask application
│   ├── __init__.py              # App factory and configuration
│   ├── config.py                # Flask configuration
│   ├── models.py                # SQLAlchemy ORM models (User, Movie, DiaryEntry)
│   ├── routes.py                # View functions and request handlers
│   ├── extensions.py            # Flask extensions (db, login_manager, etc.)
│   ├── templates/               # Jinja2 HTML templates
│   └── static/                  # CSS, JavaScript, images
├── tests/                       # Test suite
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── unit_tests.py            # 17 unit tests
│   └── selenium_tests.py        # 7 acceptance tests
├── migrations/                  # SQLAlchemy migration scripts
├── instance/                    # Instance folder (database, configs)
├── run.py                       # Flask app launcher
├── seed_demo_data.py            # Demo data seeder
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .env                         # Environment variables (create locally)
```

