import requests
import json
from pathlib import Path
from time import sleep
from typing import List, Dict


def _get_with_retries(url: str, timeout: int = 10, retries: int = 2, backoff: float = 0.5):
    attempt = 0
    while attempt <= retries:
        try:
            resp = requests.get(url, timeout=timeout)
            return resp
        except requests.RequestException:
            attempt += 1
            if attempt > retries:
                raise
            sleep(backoff * attempt)


def fetch_movie_credits(api_key: str, movie_id: int) -> Dict:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
    try:
        response = _get_with_retries(url)
        if response.status_code == 200:
            credits = response.json()
            directors = [m["name"] for m in credits.get("crew", []) if m.get("job") == "Director"]
            cast = [a["name"] for a in credits.get("cast", [])[:5]]
            return {"director": " | ".join(directors) or None, "cast": cast}
        return {"director": None, "cast": []}
    except requests.RequestException:
        return {"director": None, "cast": []}


def fetch_movie_data(api_key: str, movie_ids: List[int]) -> List[Dict]:
    base_url = "https://api.themoviedb.org/3/movie/"
    movies_data: List[Dict] = []

    for movie_id in movie_ids:
        try:
            response = _get_with_retries(f"{base_url}{movie_id}?api_key={api_key}")
            if response.status_code == 200:
                movie = response.json()
                credits = fetch_movie_credits(api_key, movie_id)
                movie.update(credits)
                movies_data.append(movie)
            else:
                continue
        except requests.RequestException:
            continue

    data_path = Path(__file__).resolve().parents[2] / "data"
    data_path.mkdir(exist_ok=True, parents=True)
    output_file = data_path / "movies_raw.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(movies_data, f, indent=4, ensure_ascii=False)

    return movies_data
