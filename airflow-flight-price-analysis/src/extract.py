import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_ROOT / "data" / "Flight_Price_Dataset_of_Bangladesh.csv"


def extract_flight_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    raw_path = PROJECT_ROOT / "data" / "raw_flights.csv"
    df.to_csv(raw_path, index=False)

    return df
