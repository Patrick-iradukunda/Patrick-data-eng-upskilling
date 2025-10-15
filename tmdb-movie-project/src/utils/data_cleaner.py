import pandas as pd
import json
from pathlib import Path
from typing import  Union


def load_raw_data() -> pd.DataFrame:
    
    data_path = Path(__file__).resolve().parents[2] / "data" / "movies_raw.json"
    with open(data_path, "r", encoding="utf-8") as file:
        movies = json.load(file)
    return pd.DataFrame(movies)


def extract_names(data: Union[list, dict, None], key: str) -> str:
    
    if isinstance(data, list):
        return " | ".join(item.get(key, "") for item in data if item.get(key))
    if isinstance(data, dict):
        return data.get("name", "")
    return ""


def convert_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_movie_data(df: pd.DataFrame) -> pd.DataFrame:
   
    irrelevant_cols = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    df.drop(columns=[col for col in irrelevant_cols if col in df.columns], inplace=True, errors='ignore')

    
    json_fields = {
        "belongs_to_collection": "name",
        "genres": "name",
        "spoken_languages": "english_name",
        "production_countries": "name",
        "production_companies": "name"
    }

    for col, key in json_fields.items():
        if col in df.columns:
            df[col] = df[col].apply(lambda x: extract_names(x, key))

    
    numeric_columns = ["budget", "revenue", "popularity"]
    df = convert_numeric(df, numeric_columns)

   
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

   
    desired_order = [
        'id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
        'original_language', 'budget_musd', 'revenue_musd', 'production_companies',
        'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime',
        'overview', 'spoken_languages', 'poster_path'
    ]

    existing_columns = [col for col in desired_order if col in df.columns]
    df = df[existing_columns]

   
    cleaned_path = Path(__file__).resolve().parents[2] / "data" / "movies_cleaned.csv"
    df.to_csv(cleaned_path, index=False)
    print(f" Cleaned data saved to {cleaned_path}")
    return df
