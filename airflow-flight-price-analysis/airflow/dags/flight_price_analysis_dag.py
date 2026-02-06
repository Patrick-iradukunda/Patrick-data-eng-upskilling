import sys
from pathlib import Path
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.extract import extract_flight_data
from src.validate import validate_data
from src.transform import transform_data
from src.kpi import compute_kpis
from src.load_mysql import load_to_mysql
from src.load_postgres import load_to_postgres


def run_pipeline():
    print("[PIPELINE] Starting ETL...")

    df = extract_flight_data()
    print(f"[EXTRACT] rows extracted: {len(df)}")

    df = validate_data(df)
    print(f"[VALIDATE] rows after validation: {len(df)}")

    df = transform_data(df)
    print("[TRANSFORM] completed")

    load_to_mysql(df, table_name="flight_prices_raw")
    load_to_mysql(df, table_name="flight_prices_staging")
    print("[MYSQL] Load complete")

    airline_kpis, routes, seasonal = compute_kpis(df)
    print("[KPI] Computation complete")

    load_to_postgres(airline_kpis, routes, seasonal)
    print("[POSTGRES] Load complete")

    print("[PIPELINE] Finished successfully!")


with DAG(
    dag_id="flight_price_analysis",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["flight", "etl", "analytics"],
) as dag:

    run_pipeline_task = PythonOperator(
        task_id="run_pipeline",
        python_callable=run_pipeline
    )
