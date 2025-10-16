import requests
import json
from pathlib import Path


def fetch_movie_credits(api_key: str, movie_id: int) -> dict:
    # Fetch cast and crew (director) from TMDB API.
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            credits = response.json()
            directors = [m["name"] for m in credits.get("crew", []) if m.get("job") == "Director"]
            cast = [a["name"] for a in credits.get("cast", [])[:5]]
            return {"director": " | ".join(directors) or None, "cast": cast}
        print(f"⚠️  Failed to fetch credits for movie {movie_id}: HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"⚠️  Error fetching credits for movie {movie_id}: {e}")
    return {"director": None, "cast": []}


def fetch_movie_data(api_key: str, movie_ids: list[int]) -> list[dict]:
    # Fetch movie data and credits from TMDB API.
    base_url = "https://api.themoviedb.org/3/movie/"
    movies_data = []

    for movie_id in movie_ids:
        try:
            response = requests.get(f"{base_url}{movie_id}?api_key={api_key}", timeout=10)
            if response.status_code == 200:
                movie = response.json()
                credits = fetch_movie_credits(api_key, movie_id)
                movie.update(credits)
                movies_data.append(movie)
            else:
                print(f"⚠️  Skipping movie ID {movie_id}: HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"⚠️  Error fetching movie {movie_id}: {e}")

    data_path = Path(__file__).resolve().parents[2] / "data"
    data_path.mkdir(exist_ok=True, parents=True)
    output_file = data_path / "movies_raw.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(movies_data, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(movies_data)} movies to {output_file}")
    return movies_data
