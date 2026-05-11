#!/usr/bin/env python3
"""Fetch top TMDB poster for titles in the database and save locally.

This script searches themoviedb.org for each movie/title, grabs the first
result's poster (from the page's `og:image`), saves it under
`static/images/posters/tmdb/` and updates `Movie.poster_path` and any
`DiaryEntry` rows that reference the same title.

Usage:
    source .venv/bin/activate
    python scripts/fetch_tmdb_posters.py
"""
from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from moviehub import create_app, db
from moviehub.models import Movie, DiaryEntry


BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "static" / "images" / "posters" / "tmdb"
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MovieHubPosterBot/1.0)"}


def slugify(value: str) -> str:
    normalized = "".join((c.lower() if c.isalnum() else "-") for c in value)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")


def get_tmdb_first_result_url(title: str) -> str | None:
    url = f"https://www.themoviedb.org/search?query={quote_plus(title)}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    anchor = soup.find("a", href=re.compile(r"^/(movie|tv)/\d+"))
    if anchor:
        href = anchor.get("href")
        return urljoin("https://www.themoviedb.org", href)
    return None


def get_poster_url_from_tmdb_page(page_url: str) -> str | None:
    r = requests.get(page_url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    meta = soup.find("meta", property="og:image")
    if meta and meta.get("content"):
        return meta["content"]
    img = soup.find("img", class_=re.compile("poster"))
    if img and img.get("src"):
        return img["src"]
    return None


def download_image(url: str, dest_path: Path) -> None:
    r = requests.get(url, headers=HEADERS, stream=True, timeout=30)
    r.raise_for_status()
    with open(dest_path, "wb") as fh:
        for chunk in r.iter_content(8192):
            fh.write(chunk)


def main() -> None:
    app = create_app()
    with app.app_context():
        # Find movies that likely still have generated SVG placeholders.
        movies = Movie.query.order_by(Movie.id).all()
        to_process = [m for m in movies if not m.poster_path or m.poster_path.endswith(".svg")]
        print(f"Found {len(to_process)} records to process")

        for idx, movie in enumerate(to_process, start=1):
            title = movie.title
            print(f"[{idx}/{len(to_process)}] {title}")
            try:
                result_url = get_tmdb_first_result_url(title)
                if not result_url:
                    print("  no TMDB search result; skipping")
                    continue

                poster_url = get_poster_url_from_tmdb_page(result_url)
                if not poster_url:
                    print("  no poster found on TMDB page; skipping")
                    continue

                slug = slugify(title)
                filename = f"{slug}.jpg"
                out_path = OUT_DIR / filename
                if out_path.exists():
                    print(f"  already exists: {out_path.name}")
                else:
                    print(f"  downloading poster from {poster_url}")
                    download_image(poster_url, out_path)
                    time.sleep(0.8)

                rel_path = f"/static/images/posters/tmdb/{filename}"
                movie.poster_path = rel_path
                DiaryEntry.query.filter_by(title=movie.title).update({"poster_path": rel_path})
                db.session.add(movie)
                db.session.commit()
                print(f"  saved and updated DB -> {rel_path}")
            except Exception as exc:
                print("  error:", exc)
                db.session.rollback()


if __name__ == "__main__":
    main()
