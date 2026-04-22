# AGENTS.md

Instructions for AI coding agents working in this repository.

## Start Here

- Read the main project context in [README.md](README.md).
- Treat top-level code as canonical app code:
  - `app.py`
  - `templates/`
  - `static/`
  - `pages/`
- There is a nested folder `cits3403-group-project/` with prototype/duplicate files. Do not modify nested duplicates unless the task explicitly targets them.

## Chat History First

- Before editing, use the current chat history as the source of truth for in-scope requirements and decisions.
- Do not re-open settled decisions from earlier messages unless new constraints conflict.
- If requirements are ambiguous or conflicting, state the conflict and propose one concrete resolution.

## Run And Verify

- Run locally with:
  - `python app.py`
- Current app is a small Flask server with routes for `/` and `/about`.
- No formal automated test suite is currently present; do targeted manual verification for changed flows.

## Project Conventions

- Backend: Flask + Jinja templates.
- Frontend: plain HTML/CSS/JavaScript (no frontend framework currently in use).
- In templates, reference assets through Jinja helpers (for example `url_for('static', filename='style.css')`) instead of hard-coded absolute paths.
- Keep changes minimal and aligned with existing style.

## Known Gaps To Keep In Mind

- Root `README.md` describes planned features that are not fully implemented yet.
- Dependency pinning is not set up (`requirements.txt` is currently missing).
- Repository currently has limited setup/test documentation.

## Related Docs

- Main project description: [README.md](README.md)
- Secondary/older project readme in nested folder: [cits3403-group-project/README.md](cits3403-group-project/README.md)