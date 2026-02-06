import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INPUT_CSV = DATA_DIR / "Flight_Price_Dataset_of_Bangladesh.csv"

def extract_flight_data():
    print("[EXTRACT] Starting extraction...")
    df = pd.read_csv(INPUT_CSV)
    print(f"[EXTRACT] rows extracted: {len(df)}")
    print("[EXTRACT] Data sample BEFORE validation:")
    print(df.head())
    return df

if __name__ == "__main__":
    df = extract_flight_data()
    print("[EXTRACT] Data sample:")
    print(df.head())