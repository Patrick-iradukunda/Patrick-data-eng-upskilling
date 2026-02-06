import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "Pazzoti99%"
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "flight_analytics"

def get_postgres_engine():
    """
    Create a SQLAlchemy 2.0 compatible PostgreSQL engine.
    """
    return create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        pool_pre_ping=True,
        pool_recycle=3600,
        future=True
    )

def load_to_postgres(
    airline_kpis: pd.DataFrame,
    routes: pd.DataFrame,
    seasonal: pd.DataFrame
):
    """
    Load KPI DataFrames into PostgreSQL.

    Tables:
    - airline_kpis
    - top_routes
    - seasonal_trends
    """
    engine = get_postgres_engine()

   
    airline_kpis.columns = [c.strip().lower().replace(" ", "_") for c in airline_kpis.columns]
    routes.columns = [c.strip().lower().replace(" ", "_") for c in routes.columns]
    seasonal.columns = [c.strip().lower().replace(" ", "_") for c in seasonal.columns]

    airline_kpis.to_sql(
        "airline_kpis",
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000
    )

    routes.to_sql(
        "top_routes",
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000
    )

    seasonal.to_sql(
        "seasonal_trends",
        con=engine,
        if_exists="replace",
        index=False,
        method="multi",
        chunksize=1000
    )

    print("[LOAD POSTGRES] KPI tables loaded successfully!")
