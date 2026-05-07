# Database Migrations (Alembic / Flask-Migrate)

This project uses Flask-Migrate (Alembic) to version database schema changes. Migration files record schema changes and are committed to Git; the actual database file lives in `instance/` and is ignored by Git.

Quick commands (development)

1. Set the Flask app environment variable

```bash
export FLASK_APP=run.py
```

2. Initialize migrations (only once)

```bash
./.venv/bin/flask db init
```

3. Generate a migration after changing models

```bash
./.venv/bin/flask db migrate -m "describe changes"
```

4. Apply migrations to the local database

```bash
./.venv/bin/flask db upgrade
```

5. To revert the last migration (use with caution)

```bash
./.venv/bin/flask db downgrade -1
```

Best practices

- Keep your `instance/` directory and any `*.db` files out of Git (already in `.gitignore`).
- Commit the generated migration files under `migrations/versions/` so teammates and CI can apply the same schema changes.
- Plan your tables and relationships up front to minimize disruptive migrations.
- For production use a managed DB (Postgres) and set `DATABASE_URL` in the environment rather than using the local SQLite file.

Notes

- If Alembic reports "No changes in schema detected", your models and current DB schema already match.
- If you need a clean baseline on a fresh machine, clone the repo, create a local `.env` (see `.env.example`), then run `flask db upgrade` to create the schema.

Examples (one-line)

```bash
export FLASK_APP=run.py && ./.venv/bin/flask db migrate -m "add field to User" && ./.venv/bin/flask db upgrade
```

That's it — migrations record schema changes while your database file remains local and out of Git.
