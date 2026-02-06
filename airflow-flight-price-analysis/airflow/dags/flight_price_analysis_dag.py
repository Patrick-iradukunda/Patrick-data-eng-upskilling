import sys
from pathlib import Path
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from src.extract import extract_flight_data
from src.validate import validate_data
from src.transform import transform_data
from src.kpi import compute_kpis
from src.load_mysql import load_to_mysql
from src.load_postgres import load_to_postgres


def run_pipeline():
    df = extract_flight_data()
    df = validate_data(df)
    df = transform_data(df)

    load_to_mysql(df)

    airline_kpis, routes, seasonal = compute_kpis(df)
    load_to_postgres(airline_kpis, routes, seasonal)


with DAG(
    dag_id="flight_price_analysis",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["flight", "etl", "analytics"],
) as dag:

    run_pipeline_task = PythonOperator(
        task_id="run_pipeline",
        python_callable=run_pipeline
    )
