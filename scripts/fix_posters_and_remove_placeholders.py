#!/usr/bin/env python3
"""Replace SVG placeholder poster paths with downloaded TMDB JPGs and remove unused SVGs."""
import os
import re
from pathlib import Path

from moviehub import create_app, db
from moviehub.models import Movie, DiaryEntry


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def main():
    app = create_app()
    project_root = Path(__file__).resolve().parent.parent
    tmdb_dir = project_root / "static" / "images" / "posters" / "tmdb"
    posters_dir = project_root / "static" / "images" / "posters"

    updated_movies = 0
    updated_diary = 0

    with app.app_context():
        movies = Movie.query.all()
        for m in movies:
            if not m.poster_path or (isinstance(m.poster_path, str) and m.poster_path.lower().endswith('.svg')):
                slug = slugify(m.title)
                candidate = tmdb_dir / f"{slug}.jpg"
                if candidate.exists():
                    m.poster_path = f"/static/images/posters/tmdb/{slug}.jpg"
                    db.session.add(m)
                    updated_movies += 1
        if updated_movies:
            db.session.commit()

        entries = DiaryEntry.query.all()
        for e in entries:
            if not e.poster_path or (isinstance(e.poster_path, str) and e.poster_path.lower().endswith('.svg')):
                # try to use matching Movie first
                movie = Movie.query.filter_by(title=e.title).first()
                if movie and movie.poster_path:
                    e.poster_path = movie.poster_path
                    db.session.add(e)
                    updated_diary += 1
                    continue

                slug = slugify(e.title)
                candidate = tmdb_dir / f"{slug}.jpg"
                if candidate.exists():
                    e.poster_path = f"/static/images/posters/tmdb/{slug}.jpg"
                    db.session.add(e)
                    updated_diary += 1

        if updated_diary:
            db.session.commit()

        print(f"Updated movies: {updated_movies}, diary entries: {updated_diary}")

        # Build referenced web paths set
        referenced = set()
        for (p,) in Movie.query.with_entities(Movie.poster_path):
            if p:
                referenced.add(os.path.normpath(p))
        for (p,) in DiaryEntry.query.with_entities(DiaryEntry.poster_path):
            if p:
                referenced.add(os.path.normpath(p))

        deleted = 0
        # scan posters_dir for svg files (excluding tmdb folder)
        for p in posters_dir.glob('**/*.svg'):
            # skip svgs in tmdb (shouldn't be any) and ensure inside posters_dir
            if 'tmdb' in p.parts:
                continue
            try:
                rel = os.path.normpath(str(p.relative_to(project_root)))
            except Exception:
                rel = os.path.normpath(str(p))
            web_path = f"/{rel.replace(os.path.sep, '/')}"
            if os.path.normpath(web_path) not in referenced:
                try:
                    p.unlink()
                    deleted += 1
                except Exception as ex:
                    print('Failed to delete', p, ex)

        print(f"Deleted unused SVG placeholders: {deleted}")


if __name__ == '__main__':
    main()
