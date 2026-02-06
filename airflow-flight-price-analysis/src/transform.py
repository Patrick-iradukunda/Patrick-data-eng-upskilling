def transform_data(df):
    df = df.copy()
    df["price"] = df["price"].astype(float)
    df["duration"] = df["duration"].astype(float)
    df["days_left"] = df["days_left"].astype(int)
    return df

if __name__ == "__main__":
    import sys
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(PROJECT_ROOT))

    from src.extract import extract_flight_data
    from src.validate import validate_data

    df = extract_flight_data()
    df = validate_data(df)
    df = transform_data(df)
    print("[TRANSFORM] Sample data AFTER transformation:")
    print(df.head())
