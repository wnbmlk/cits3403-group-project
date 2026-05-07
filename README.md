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

- HTML
- CSS
- JavaScript
- Flask

## Environment Variables

Create a local `.env` file based on `.env.example` and keep it out of Git.

- `SECRET_KEY`: Flask session secret, used for signed cookies and flash/session security.
- `DATABASE_URL`: Database connection string. For local development, use `sqlite:///instance/moviehub.db`. For a shared database, point this to a hosted PostgreSQL URL.

Passwords are hashed with Werkzeug before storage. The secret key is not used to store or recover passwords.

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
