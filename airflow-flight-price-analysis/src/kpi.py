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

    df["season"] = "non_peak"
    seasonal_fares = (
        df.groupby("season")
        .agg(avg_fare=("price", "mean"))
        .reset_index()
    )

    return airline_kpis, popular_routes, seasonal_fares
