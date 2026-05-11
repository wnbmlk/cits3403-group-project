from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

from moviehub import create_app, db
from moviehub.models import DiaryEntry, Movie, User


BASE_DIR = Path(__file__).resolve().parent
POSTER_DIR = BASE_DIR / "static" / "images" / "posters"


MOVIES = [
    ("The Shawshank Redemption", "Movie"),
    ("The Godfather", "Movie"),
    ("The Godfather Part II", "Movie"),
    ("The Dark Knight", "Movie"),
    ("12 Angry Men", "Movie"),
    ("Schindler's List", "Movie"),
    ("Pulp Fiction", "Movie"),
    ("The Lord of the Rings: The Return of the King", "Movie"),
    ("The Good, the Bad and the Ugly", "Movie"),
    ("Fight Club", "Movie"),
    ("Forrest Gump", "Movie"),
    ("Inception", "Movie"),
    ("The Matrix", "Movie"),
    ("Goodfellas", "Movie"),
    ("Seven Samurai", "Movie"),
    ("Parasite", "Movie"),
    ("Interstellar", "Movie"),
    ("City of God", "Movie"),
    ("The Silence of the Lambs", "Movie"),
    ("Saving Private Ryan", "Movie"),
    ("Spirited Away", "Movie"),
    ("Whiplash", "Movie"),
    ("The Green Mile", "Movie"),
    ("Se7en", "Movie"),
    ("Gladiator", "Movie"),
    ("Casablanca", "Movie"),
    ("The Departed", "Movie"),
    ("The Prestige", "Movie"),
    ("The Pianist", "Movie"),
    ("Back to the Future", "Movie"),
    ("Apocalypse Now", "Movie"),
    ("Alien", "Movie"),
    ("Terminator 2: Judgment Day", "Movie"),
    ("Raiders of the Lost Ark", "Movie"),
    ("The Lion King", "Movie"),
    ("The Usual Suspects", "Movie"),
    ("Memento", "Movie"),
    ("Django Unchained", "Movie"),
    ("Toy Story", "Movie"),
    ("Joker", "Movie"),
    ("Avengers: Endgame", "Movie"),
    ("The Truman Show", "Movie"),
    ("Blade Runner 2049", "Movie"),
    ("No Country for Old Men", "Movie"),
    ("Oldboy", "Movie"),
    ("Come and See", "Movie"),
    ("La La Land", "Movie"),
    ("There Will Be Blood", "Movie"),
    ("Eternal Sunshine of the Spotless Mind", "Movie"),
    ("The Lord of the Rings: The Fellowship of the Ring", "Movie"),
]

# Top 50 TV series — kept as separate list but will be seeded as movies with genre 'TV'
TV_SERIES = [
    ("Breaking Bad", "TV"),
    ("The Wire", "TV"),
    ("The Sopranos", "TV"),
    ("Band of Brothers", "TV"),
    ("Chernobyl", "TV"),
    ("Better Call Saul", "TV"),
    ("Game of Thrones", "TV"),
    ("The Office", "TV"),
    ("Friends", "TV"),
    ("Succession", "TV"),
    ("Mad Men", "TV"),
    ("Fleabag", "TV"),
    ("True Detective", "TV"),
    ("Sherlock", "TV"),
    ("Dark", "TV"),
    ("Stranger Things", "TV"),
    ("The Bear", "TV"),
    ("Arcane", "TV"),
    ("Attack on Titan", "TV"),
    ("The Last of Us", "TV"),
    ("Severance", "TV"),
    ("Black Mirror", "TV"),
    ("Mindhunter", "TV"),
    ("Narcos", "TV"),
    ("Peaky Blinders", "TV"),
    ("House", "TV"),
    ("The Boys", "TV"),
    ("BoJack Horseman", "TV"),
    ("Rick and Morty", "TV"),
    ("Mr. Robot", "TV"),
    ("The Crown", "TV"),
    ("Lost", "TV"),
    ("The Leftovers", "TV"),
    ("Six Feet Under", "TV"),
    ("The Mandalorian", "TV"),
    ("Dexter", "TV"),
    ("Ozark", "TV"),
    ("The Haunting of Hill House", "TV"),
    ("Prison Break", "TV"),
    ("Avatar: The Last Airbender", "TV"),
    ("The West Wing", "TV"),
    ("Twin Peaks", "TV"),
    ("The X-Files", "TV"),
    ("Fargo", "TV"),
    ("The Queen's Gambit", "TV"),
    ("When They See Us", "TV"),
    ("Cosmos", "TV"),
    ("Blue Eye Samurai", "TV"),
    ("Shōgun", "TV"),
    ("The Simpsons", "TV"),
]

ANIME = [
    ("Fullmetal Alchemist: Brotherhood", "Anime"),
    ("Attack on Titan", "Anime"),
    ("Death Note", "Anime"),
    ("Steins;Gate", "Anime"),
    ("Hunter x Hunter", "Anime"),
    ("One Piece", "Anime"),
    ("Naruto", "Anime"),
    ("Naruto: Shippuden", "Anime"),
    ("Bleach", "Anime"),
    ("Demon Slayer: Kimetsu no Yaiba", "Anime"),
    ("Jujutsu Kaisen", "Anime"),
    ("Vinland Saga", "Anime"),
    ("Monster", "Anime"),
    ("Code Geass", "Anime"),
    ("Cowboy Bebop", "Anime"),
    ("Neon Genesis Evangelion", "Anime"),
    ("Frieren: Beyond Journey's End", "Anime"),
    ("Mob Psycho 100", "Anime"),
    ("One Punch Man", "Anime"),
    ("Haikyuu!!", "Anime"),
    ("Kaguya-sama: Love Is War", "Anime"),
    ("Your Lie in April", "Anime"),
    ("Clannad: After Story", "Anime"),
    ("Made in Abyss", "Anime"),
    ("Psycho-Pass", "Anime"),
    ("Samurai Champloo", "Anime"),
    ("Parasyte: The Maxim", "Anime"),
    ("Re:Zero − Starting Life in Another World", "Anime"),
    ("Gintama", "Anime"),
    ("Berserk", "Anime"),
    ("JoJo's Bizarre Adventure", "Anime"),
    ("Chainsaw Man", "Anime"),
    ("Dragon Ball Z", "Anime"),
    ("Spy × Family", "Anime"),
    ("Black Clover", "Anime"),
    ("Mushoku Tensei: Jobless Reincarnation", "Anime"),
    ("Erased", "Anime"),
    ("Bocchi the Rock!", "Anime"),
    ("Blue Lock", "Anime"),
    ("86", "Anime"),
    ("Spirited Away", "Anime"),
    ("Your Name", "Anime"),
    ("A Silent Voice", "Anime"),
    ("Princess Mononoke", "Anime"),
    ("Akira", "Anime"),
    ("Howl's Moving Castle", "Anime"),
    ("Grave of the Fireflies", "Anime"),
    ("Perfect Blue", "Anime"),
    ("Ghost in the Shell", "Anime"),
    ("The Boy and the Heron", "Anime"),
]


# Genre mapping for all titles (extracted from actual content)
TITLE_GENRES = {
    "The Shawshank Redemption": "Drama",
    "The Godfather": "Crime, Drama",
    "The Godfather Part II": "Crime, Drama",
    "The Dark Knight": "Action, Crime",
    "12 Angry Men": "Drama",
    "Schindler's List": "Drama, History",
    "Pulp Fiction": "Crime, Drama",
    "The Lord of the Rings: The Return of the King": "Fantasy, Adventure",
    "The Good, the Bad and the Ugly": "Western",
    "Fight Club": "Drama, Thriller",
    "Forrest Gump": "Drama, Romance",
    "Inception": "Sci-Fi, Thriller",
    "The Matrix": "Sci-Fi, Action",
    "Goodfellas": "Crime, Drama",
    "Seven Samurai": "Action, Adventure",
    "Parasite": "Thriller, Drama",
    "Interstellar": "Sci-Fi, Adventure",
    "City of God": "Crime, Drama",
    "The Silence of the Lambs": "Thriller, Crime",
    "Saving Private Ryan": "War, Drama",
    "Spirited Away": "Animation, Fantasy",
    "Whiplash": "Drama",
    "The Green Mile": "Drama, Fantasy",
    "Se7en": "Thriller, Crime",
    "Gladiator": "Action, Adventure",
    "Casablanca": "Romance, Drama",
    "The Departed": "Crime, Thriller",
    "The Prestige": "Drama, Mystery",
    "The Pianist": "Drama, War",
    "Back to the Future": "Adventure, Sci-Fi",
    "Apocalypse Now": "War, Drama",
    "Alien": "Horror, Sci-Fi",
    "Terminator 2: Judgment Day": "Action, Sci-Fi",
    "Raiders of the Lost Ark": "Adventure, Action",
    "The Lion King": "Animation, Adventure",
    "The Usual Suspects": "Crime, Thriller",
    "Memento": "Mystery, Thriller",
    "Django Unchained": "Western, Drama",
    "Toy Story": "Animation, Comedy",
    "Joker": "Crime, Drama",
    "Avengers: Endgame": "Action, Adventure",
    "The Truman Show": "Drama, Sci-Fi",
    "Blade Runner 2049": "Sci-Fi, Thriller",
    "No Country for Old Men": "Crime, Thriller",
    "Oldboy": "Thriller, Action",
    "Come and See": "War, Drama",
    "La La Land": "Romance, Musical",
    "There Will Be Blood": "Drama",
    "Eternal Sunshine of the Spotless Mind": "Romance, Sci-Fi",
    "The Lord of the Rings: The Fellowship of the Ring": "Fantasy, Adventure",
    "Breaking Bad": "Crime, Drama",
    "The Wire": "Crime, Drama",
    "The Sopranos": "Crime, Drama",
    "Band of Brothers": "War, Drama",
    "Chernobyl": "Drama, History",
    "Better Call Saul": "Crime, Drama",
    "Game of Thrones": "Fantasy, Drama",
    "The Office": "Comedy",
    "Friends": "Comedy, Romance",
    "Succession": "Drama",
    "Mad Men": "Drama",
    "Fleabag": "Comedy, Drama",
    "True Detective": "Crime, Drama",
    "Sherlock": "Crime, Mystery",
    "Dark": "Sci-Fi, Thriller",
    "Stranger Things": "Sci-Fi, Adventure",
    "The Bear": "Drama, Comedy",
    "Arcane": "Animation, Action",
    "Attack on Titan": "Animation, Action",
    "The Last of Us": "Drama, Sci-Fi",
    "Severance": "Sci-Fi, Thriller",
    "Black Mirror": "Sci-Fi, Thriller",
    "Mindhunter": "Crime, Thriller",
    "Narcos": "Crime, Drama",
    "Peaky Blinders": "Crime, Drama",
    "House": "Drama, Mystery",
    "The Boys": "Action, Comedy",
    "BoJack Horseman": "Animation, Comedy",
    "Rick and Morty": "Animation, Sci-Fi",
    "Mr. Robot": "Thriller, Drama",
    "The Crown": "Drama, History",
    "Lost": "Adventure, Drama",
    "The Leftovers": "Drama, Fantasy",
    "Six Feet Under": "Drama",
    "The Mandalorian": "Sci-Fi, Adventure",
    "Dexter": "Crime, Drama",
    "Ozark": "Crime, Drama",
    "The Haunting of Hill House": "Horror, Drama",
    "Prison Break": "Thriller, Crime",
    "Avatar: The Last Airbender": "Animation, Adventure",
    "The West Wing": "Drama",
    "Twin Peaks": "Mystery, Drama",
    "The X-Files": "Mystery, Sci-Fi",
    "Fargo": "Crime, Drama",
    "The Queen's Gambit": "Drama, Sport",
    "When They See Us": "Drama, History",
    "Cosmos": "Documentary",
    "Blue Eye Samurai": "Animation, Action",
    "Shōgun": "Drama, History",
    "The Simpsons": "Animation, Comedy",
    "Fullmetal Alchemist: Brotherhood": "Animation, Adventure",
    "Death Note": "Animation, Thriller",
    "Steins;Gate": "Animation, Sci-Fi",
    "Hunter x Hunter": "Animation, Adventure",
    "One Piece": "Animation, Adventure",
    "Naruto": "Animation, Action",
    "Naruto: Shippuden": "Animation, Action",
    "Bleach": "Animation, Action",
    "Demon Slayer: Kimetsu no Yaiba": "Animation, Action",
    "Jujutsu Kaisen": "Animation, Action",
    "Vinland Saga": "Animation, Drama",
    "Monster": "Animation, Thriller",
    "Code Geass": "Animation, Sci-Fi",
    "Cowboy Bebop": "Animation, Sci-Fi",
    "Neon Genesis Evangelion": "Animation, Sci-Fi",
    "Frieren: Beyond Journey's End": "Animation, Fantasy",
    "Mob Psycho 100": "Animation, Comedy",
    "One Punch Man": "Animation, Action",
    "Haikyuu!!": "Animation, Sport",
    "Kaguya-sama: Love Is War": "Animation, Comedy",
    "Your Lie in April": "Animation, Drama",
    "Clannad: After Story": "Animation, Drama",
    "Made in Abyss": "Animation, Adventure",
    "Psycho-Pass": "Animation, Sci-Fi",
    "Samurai Champloo": "Animation, Action",
    "Parasyte: The Maxim": "Animation, Horror",
    "Re:Zero − Starting Life in Another World": "Animation, Fantasy",
    "Gintama": "Animation, Comedy",
    "Berserk": "Animation, Fantasy",
    "JoJo's Bizarre Adventure": "Animation, Action",
    "Chainsaw Man": "Animation, Action",
    "Dragon Ball Z": "Animation, Action",
    "Spy × Family": "Animation, Comedy",
    "Black Clover": "Animation, Fantasy",
    "Mushoku Tensei: Jobless Reincarnation": "Animation, Fantasy",
    "Erased": "Animation, Thriller",
    "Bocchi the Rock!": "Animation, Comedy",
    "Blue Lock": "Animation, Sport",
    "86": "Animation, Sci-Fi",
    "Your Name": "Animation, Romance",
    "A Silent Voice": "Animation, Drama",
    "Princess Mononoke": "Animation, Fantasy",
    "Akira": "Animation, Sci-Fi",
    "Howl's Moving Castle": "Animation, Fantasy",
    "Grave of the Fireflies": "Animation, War",
    "Perfect Blue": "Animation, Thriller",
    "Ghost in the Shell": "Animation, Sci-Fi",
    "The Boy and the Heron": "Animation, Fantasy",
}


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
        title, media_type = items[index % len(items)]
        if index >= len(items):
            title = f"{title} {index + 1 - len(items)}"

        accent, base = build_palette(start_index + index)
        slug = slugify(title)
        poster_name = f"{label}-{index + 1:03d}-{slug}.svg"
        genre = TITLE_GENRES.get(title, "")
        
        records.append(
            {
                "title": title,
                "media_type": media_type,
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
            movie.media_type = record["media_type"]
            movie.genre = record["genre"]
            movie.status = record["status"]
            movie.poster_path = record["poster_path"]
            continue

        db.session.add(
            Movie(
                title=record["title"],
                media_type=record["media_type"],
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
                media_type=record["media_type"],
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

        combined_movies = MOVIES + TV_SERIES
        movie_records = expand_records(combined_movies, "movie", len(combined_movies))
        anime_records = expand_records(ANIME, "anime", len(ANIME), start_index=len(combined_movies))
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