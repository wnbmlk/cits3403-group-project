from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

from moviehub import create_app, db
from moviehub.models import DiaryEntry, Movie, User


BASE_DIR = Path(__file__).resolve().parent
POSTER_DIR = BASE_DIR / "static" / "images" / "posters"


MOVIES = [
    ("The Shawshank Redemption", "Drama"),
    ("The Godfather", "Crime"),
    ("The Dark Knight", "Action"),
    ("Pulp Fiction", "Crime"),
    ("Forrest Gump", "Drama"),
    ("Inception", "Sci-Fi"),
    ("Interstellar", "Sci-Fi"),
    ("Fight Club", "Drama"),
    ("The Matrix", "Sci-Fi"),
    ("Gladiator", "Action"),
    ("Spirited Away", "Animation"),
    ("The Lion King", "Animation"),
    ("Parasite", "Thriller"),
    ("Whiplash", "Drama"),
    ("Se7en", "Thriller"),
    ("The Prestige", "Mystery"),
    ("The Departed", "Crime"),
    ("Avatar", "Adventure"),
    ("Titanic", "Romance"),
    ("Joker", "Drama"),
    ("Mad Max: Fury Road", "Action"),
    ("Black Panther", "Action"),
    ("La La Land", "Musical"),
    ("The Social Network", "Drama"),
    ("Dune", "Sci-Fi"),
    ("Dune: Part Two", "Sci-Fi"),
    ("Oppenheimer", "Biography"),
    ("Top Gun: Maverick", "Action"),
    ("Her", "Romance"),
    ("Arrival", "Sci-Fi"),
]

ANIME = [
    ("Naruto", "Shonen"),
    ("Naruto Shippuden", "Shonen"),
    ("One Piece", "Adventure"),
    ("Bleach", "Shonen"),
    ("Attack on Titan", "Dark Fantasy"),
    ("Fullmetal Alchemist: Brotherhood", "Adventure"),
    ("Death Note", "Thriller"),
    ("Demon Slayer", "Action"),
    ("Jujutsu Kaisen", "Action"),
    ("My Hero Academia", "Shonen"),
    ("Chainsaw Man", "Action"),
    ("Spy x Family", "Comedy"),
    ("Hunter x Hunter", "Adventure"),
    ("Tokyo Ghoul", "Dark Fantasy"),
    ("Haikyuu!!", "Sports"),
    ("One Punch Man", "Action"),
    ("Cowboy Bebop", "Sci-Fi"),
    ("Steins;Gate", "Sci-Fi"),
    ("Your Name", "Romance"),
    ("Weathering With You", "Romance"),
    ("A Silent Voice", "Drama"),
    ("Violet Evergarden", "Drama"),
    ("Mushoku Tensei", "Fantasy"),
    ("Frieren: Beyond Journey's End", "Fantasy"),
    ("Jujutsu Kaisen 0", "Action"),
    ("Mob Psycho 100", "Supernatural"),
    ("Blue Lock", "Sports"),
    ("Vinland Saga", "Historical"),
    ("Solo Leveling", "Action"),
    ("Sailor Moon", "Magical Girl"),
]


def slugify(value: str) -> str:
    normalized = "".join(character.lower() if character.isalnum() else "-" for character in value)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")


def build_palette(index: int) -> tuple[str, str]:
    hue = (index * 29) % 360
    accent = f"hsl({hue}, 70%, 55%)"
    base = f"hsl({(hue + 24) % 360}, 45%, 18%)"
    return accent, base


def make_poster_svg(title: str, category: str, accent: str, base: str) -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='150' height='225' viewBox='0 0 150 225'>
  <defs>
    <linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>
      <stop offset='0%' stop-color='{base}'/>
      <stop offset='100%' stop-color='{accent}'/>
    </linearGradient>
  </defs>
  <rect width='150' height='225' rx='16' fill='url(#bg)'/>
  <rect x='12' y='12' width='126' height='201' rx='12' fill='rgba(255,255,255,0.08)' stroke='rgba(255,255,255,0.18)'/>
  <text x='75' y='92' text-anchor='middle' fill='white' font-family='Arial, sans-serif' font-size='14' font-weight='700'>{title}</text>
  <text x='75' y='122' text-anchor='middle' fill='rgba(255,255,255,0.85)' font-family='Arial, sans-serif' font-size='11'>{category}</text>
  <text x='75' y='186' text-anchor='middle' fill='rgba(255,255,255,0.7)' font-family='Arial, sans-serif' font-size='10'>Movie Diary Demo</text>
</svg>"""


def write_posters(records: list[dict]) -> None:
    POSTER_DIR.mkdir(parents=True, exist_ok=True)
    for record in records:
        poster_file = BASE_DIR / record["poster_path"].lstrip("/")
        poster_file.parent.mkdir(parents=True, exist_ok=True)
        poster_file.write_text(
            make_poster_svg(record["title"], record["genre"], record["accent"], record["base"]),
            encoding="utf-8",
        )


def expand_records(items: list[tuple[str, str]], label: str, count: int, start_index: int = 0) -> list[dict]:
    records: list[dict] = []
    for index in range(count):
        title, genre = items[index % len(items)]
        if index >= len(items):
            title = f"{title} {index + 1 - len(items)}"

        accent, base = build_palette(start_index + index)
        slug = slugify(title)
        poster_name = f"{label}-{index + 1:03d}-{slug}.svg"
        records.append(
            {
                "title": title,
                "genre": genre,
                "poster_path": f"/static/images/posters/{poster_name}",
                "accent": accent,
                "base": base,
            }
        )
    return records


def ensure_demo_user() -> User:
    demo_user = User.query.filter_by(username="demo").first()
    if demo_user:
        return demo_user

    demo_user = User(username="demo", password=generate_password_hash("demo-password-not-for-login"))
    db.session.add(demo_user)
    db.session.flush()
    return demo_user


def seed_movies(records: list[dict]) -> None:
    for record in records:
        movie = Movie.query.filter_by(title=record["title"]).first()
        if movie:
            movie.genre = record["genre"]
            movie.status = record["status"]
            movie.poster_path = record["poster_path"]
            continue

        db.session.add(
            Movie(
                title=record["title"],
                genre=record["genre"],
                status=record["status"],
                poster_path=record["poster_path"],
            )
        )


def seed_entries(user: User, records: list[dict], status: str, start_date: datetime) -> None:
    for index, record in enumerate(records):
        entry = DiaryEntry.query.filter_by(title=record["title"], user_id=user.id).first()
        if entry:
            continue

        db.session.add(
            DiaryEntry(
                title=record["title"],
                status=status,
                genre=record["genre"],
                poster_path=record["poster_path"],
                date=start_date + timedelta(days=index),
                user_id=user.id,
            )
        )


def main() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        movie_records = expand_records(MOVIES, "movie", 100)
        anime_records = expand_records(ANIME, "anime", 50, start_index=100)
        all_records = movie_records + anime_records
        write_posters(all_records)

        for record in movie_records:
            record["status"] = "Watched"
        for record in anime_records:
            record["status"] = "Watching"

        seed_movies(all_records)

        demo_user = ensure_demo_user()
        seed_entries(demo_user, movie_records, "Watched", datetime(2024, 1, 1))
        seed_entries(demo_user, anime_records, "Watching", datetime(2024, 5, 1))

        db.session.commit()
        print("Seeded demo data: 100 movies and 50 anime entries.")


if __name__ == "__main__":
    main()