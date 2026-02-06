import pandas as pd


REQUIRED_COLUMNS = [
    "airline",
    "source_city",
    "destination_city",
    "departure_time",
    "stops",
    "arrival_time",
    "class",
    "duration",
    "days_left",
    "price"
]

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
   
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace("&", "and")
          .str.replace(" ", "_")
    )
    return df

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
  
    df = normalize_columns(df)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

  
    df = df.dropna(subset=[
        "airline",
        "source_city",
        "destination_city",
        "price"
    ])

   
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df[df["price"] > 0]

    return df
