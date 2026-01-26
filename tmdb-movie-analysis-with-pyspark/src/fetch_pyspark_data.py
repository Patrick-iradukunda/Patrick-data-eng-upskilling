import requests
import json
import time
from pathlib import Path

# -----------------------
# API CONFIG
# -----------------------
API_KEY = "ba05b905db888a9b7e80b304cda35eba"
BASE_URL = "https://api.themoviedb.org/3/movie"

MOVIE_IDS = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513
]

# -----------------------
# ✅ CORRECT PATH HANDLING
# -----------------------
# src/fetch_pyspark_data.py -> project root -> data/
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATA_PATH = DATA_DIR / "tmdb_movies.json"

# -----------------------
# FETCH FUNCTION
# -----------------------
def fetch_movie(movie_id: int) -> dict | None:
    url = f"{BASE_URL}/{movie_id}"
    params = {"api_key": API_KEY}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"⚠️ Skipping movie_id={movie_id} (status {response.status_code})")
        return None

    return response.json()

# -----------------------
# MAIN
# -----------------------
def main():
    movies = []

    for movie_id in MOVIE_IDS:
        movie = fetch_movie(movie_id)
        if movie:
            movies.append(movie)
        time.sleep(0.25)  # be polite to the API

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(movies)} movies to {DATA_PATH}")

if __name__ == "__main__":
    main()
