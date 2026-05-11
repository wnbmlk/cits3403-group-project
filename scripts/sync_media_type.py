#!/usr/bin/env python3
"""Sync media_type from Movie catalog to DiaryEntry records."""
from moviehub import create_app, db
from moviehub.models import DiaryEntry, Movie


def main():
    app = create_app()
    with app.app_context():
        updated_entries = 0

        for entry in DiaryEntry.query.all():
            movie = Movie.query.filter(db.func.lower(Movie.title) == entry.title.lower()).first()
            if movie and movie.media_type and not entry.media_type:
                entry.media_type = movie.media_type
                updated_entries += 1

        db.session.commit()
        print(f"Updated diary entries with media_type: {updated_entries}")


if __name__ == "__main__":
    main()
