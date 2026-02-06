import pandas as pd


COLUMN_MAP = {
    "Airline": "airline",
    "Source": "source",
    "Source Name": "source_city",
    "Destination": "destination",
    "Destination Name": "destination_city",
    "Departure Date & Time": "departure_time",
    "Arrival Date & Time": "arrival_time",
    "Duration (hrs)": "duration",
    "Stopovers": "stops",
    "Aircraft Type": "aircraft_type",
    "Class": "class",
    "Booking Source": "booking_source",
    "Base Fare (BDT)": "base_fare",
    "Tax & Surcharge (BDT)": "tax",
    "Total Fare (BDT)": "price",
    "Seasonality": "season",
    "Days Before Departure": "days_left"
}

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    print("[VALIDATE] Running validation...")

    
    df = df.rename(columns=COLUMN_MAP)

   
    df["departure_time"] = pd.to_datetime(df["departure_time"], errors="coerce")
    df["arrival_time"] = pd.to_datetime(df["arrival_time"], errors="coerce")
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["days_left"] = pd.to_numeric(df["days_left"], errors="coerce", downcast="integer")

    
    required_cols = ["airline", "source_city", "destination_city", "departure_time", "arrival_time", "duration", "price", "days_left"]
    before = len(df)
    df = df.dropna(subset=required_cols)
    after = len(df)

    print(f"[VALIDATE] Rows before validation: {before}")
    print(f"[VALIDATE] Rows after validation: {after}")
    return df

if __name__ == "__main__":
    import sys
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(PROJECT_ROOT))

    from src.extract import extract_flight_data

    df = extract_flight_data()
    validated_df = validate_data(df)
    print("[VALIDATE] Sample data AFTER validation:")
    print(validated_df.head())
