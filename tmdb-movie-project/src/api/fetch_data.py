import requests
import json
from pathlib import Path

def fetch_movie_data(api_key: str, movie_ids: list[int]) -> list[dict]:
    # Fetch movie data from TMDb API for given movie IDs.
    base_url = "https://api.themoviedb.org/3/movie/"
    movies_data = []

    for movie_id in movie_ids:
        url = f"{base_url}{movie_id}?api_key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            movie = response.json()
            movies_data.append(movie)
        else:
            print(f"Skipping movie ID {movie_id}: {response.status_code}")

    # Saving raw data to data/movies_raw.json
    data_path = Path(__file__).resolve().parents[2] / "data"
    data_path.mkdir(exist_ok=True)
    with open(data_path / "movies_raw.json", "w", encoding="utf-8") as f:
        json.dump(movies_data, f, indent=4)

    print(f"Saved {len(movies_data)} movies to {data_path / 'movies_raw.json'}")
    return movies_data
