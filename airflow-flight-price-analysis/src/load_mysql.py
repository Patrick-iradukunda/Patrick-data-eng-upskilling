import pandas as pd
from sqlalchemy import create_engine

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Pazzoti99%"
DB_NAME = "flight_staging"


def get_mysql_engine():
    return create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False
    )


def load_to_mysql(df: pd.DataFrame, table_name: str):
    engine = get_mysql_engine()

    if table_name == "flight_prices_raw":
        columns_to_keep = [
            "airline", "source", "source_city", "destination", "destination_city",
            "departure_time", "arrival_time", "duration", "stops", "class",
            "base_fare", "tax", "price", "season", "days_left"
        ]
        df_renamed = df[columns_to_keep].copy()

        df_renamed["departure_time"] = pd.to_datetime(df_renamed["departure_time"], errors="coerce")
        df_renamed["arrival_time"] = pd.to_datetime(df_renamed["arrival_time"], errors="coerce")
        df_renamed["price"] = pd.to_numeric(df_renamed["price"], errors="coerce")
        df_renamed["days_left"] = pd.to_numeric(df_renamed["days_left"], errors="coerce", downcast="integer")

    elif table_name == "flight_prices_staging":
        df_renamed = pd.DataFrame({
            "airline": df["airline"],
            "source": df["source"],
            "destination": df["destination"],
            "base_fare": pd.to_numeric(df["base_fare"], errors="coerce"),
            "tax_surcharge": pd.to_numeric(df["tax"], errors="coerce"),
            "total_fare": pd.to_numeric(df["price"], errors="coerce"),
            "journey_date": pd.to_datetime(df["departure_time"], errors="coerce").dt.date,
            "aircraft_type": df.get("aircraft_type", None)
        })
    else:
        raise ValueError(f"Unknown table name: {table_name}")

    with engine.begin() as connection:
        df_renamed.to_sql(
            name=table_name,
            con=connection,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=1000
        )

    print(f"[LOAD MYSQL] {len(df_renamed)} rows loaded into '{table_name}'.")
