#!/usr/bin/env python3
"""Replace placeholder media-type labels with guessed genres in the database."""
from moviehub import create_app, db
from moviehub.models import DiaryEntry, Movie


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


def main():
    app = create_app()
    with app.app_context():
        updated_movies = 0
        updated_entries = 0

        for movie in Movie.query.all():
            genre = TITLE_GENRES.get(movie.title)
            if genre and movie.genre != genre:
                movie.genre = genre
                updated_movies += 1

        for entry in DiaryEntry.query.all():
            genre = TITLE_GENRES.get(entry.title)
            if genre and entry.genre != genre:
                entry.genre = genre
                updated_entries += 1

        db.session.commit()
        print(f"Updated movies: {updated_movies}")
        print(f"Updated diary entries: {updated_entries}")


if __name__ == "__main__":
    main()
