import pandas as pd

def compute_kpis(df):
    airline_kpis = (
        df.groupby("airline")
        .agg(
            avg_fare=("price", "mean"),
            booking_count=("price", "count")
        )
        .reset_index()
    )

    popular_routes = (
        df.groupby(["source_city", "destination_city"])
        .size()
        .reset_index(name="booking_count")
    )

    df["season"] = df.get("season", "non_peak")
    seasonal_fares = (
        df.groupby("season")
        .agg(avg_fare=("price", "mean"))
        .reset_index()
    )

    return airline_kpis, popular_routes, seasonal_fares

if __name__ == "__main__":
    import sys
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(PROJECT_ROOT))

    from src.extract import extract_flight_data
    from src.validate import validate_data
    from src.transform import transform_data

    df = extract_flight_data()
    df = validate_data(df)
    df = transform_data(df)
    airline_kpis, routes, seasonal = compute_kpis(df)

    print("[KPI] Airline KPIs:")
    print(airline_kpis.head())
    print("[KPI] Popular routes:")
    print(routes.head())
    print("[KPI] Seasonal trends:")
    print(seasonal.head())
