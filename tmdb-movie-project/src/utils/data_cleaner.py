import pandas as pd
import json
from pathlib import Path


def load_raw_data(file_path: Path = None) -> pd.DataFrame:
    # Load raw movie data from JSON file.
    if file_path is None:
        file_path = Path(__file__).resolve().parents[2] / "data" / "movies_raw.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def extract_names(data, key: str) -> str:
    # Extract names from nested JSON structures.
    if isinstance(data, list):
        return " | ".join([item.get(key, "") for item in data if item.get(key)])
    return data.get(key, "") if isinstance(data, dict) else ""


def clean_movie_data(df: pd.DataFrame) -> pd.DataFrame:
    # Clean and transform raw movie data.
    df = df.copy()
    
    df.drop(columns=['adult', 'imdb_id', 'original_title', 'video', 'homepage', 'origin_country'], 
            inplace=True, errors='ignore')

    for col, key in {"belongs_to_collection": "name", "genres": "name", "spoken_languages": "english_name",
                     "production_countries": "name", "production_companies": "name"}.items():
        if col in df.columns:
            df[col] = df[col].apply(lambda x: extract_names(x, key))

    if "cast" in df.columns:
        df["cast"] = df["cast"].apply(lambda x: " | ".join(x) if isinstance(x, list) else "")
    if "director" in df.columns:
        df["director"] = df["director"].fillna("")

    for col in ["budget", "revenue", "popularity", "vote_average", "vote_count", "runtime"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "release_date" in df.columns:
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    for col in ["budget", "revenue", "runtime"]:
        if col in df.columns:
            df.loc[df[col] == 0, col] = pd.NA

    if "budget" in df.columns:
        df["budget_musd"] = df["budget"] / 1_000_000
    if "revenue" in df.columns:
        df["revenue_musd"] = df["revenue"] / 1_000_000

    df.drop_duplicates(subset=["id", "title"], inplace=True)
    df.dropna(subset=["id", "title"], inplace=True)
    df = df[df.notna().sum(axis=1) >= 10]

    if "status" in df.columns:
        df = df[df["status"] == "Released"]
        df.drop(columns=["status"], inplace=True, errors="ignore")

    order = ['id', 'title', 'tagline', 'release_date', 'genres', 'director', 'cast',
             'belongs_to_collection', 'original_language', 'budget_musd', 'revenue_musd',
             'production_companies', 'production_countries', 'vote_count', 'vote_average',
             'popularity', 'runtime', 'overview', 'spoken_languages', 'poster_path']
    
    df = df[[col for col in order if col in df.columns]]
    
    output_path = Path(__file__).resolve().parents[2] / "data" / "movies_cleaned.csv"
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f" Cleaned data saved to {output_path}")
    return df
