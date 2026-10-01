"""
DAG chính của project: điều phối toàn bộ pipeline ETL.

Luồng chạy:
1. extract_load   -> đọc CSV, nạp vào schema raw (PostgreSQL)
2. dbt_run        -> transform: build staging views + mart tables (star schema)
3. dbt_test       -> chạy data quality tests (not_null, unique, relationships)
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "/opt/airflow/dbt_project"

default_args = {
    "owner": "data-eng",
    "retries": 1,
}

with DAG(
    dag_id="olist_etl_pipeline",
    description="ETL pipeline: extract Olist CSVs -> raw Postgres -> dbt transform -> star schema",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["portfolio", "etl", "dbt"],
) as dag:

    extract_load = BashOperator(
        task_id="extract_load",
        bash_command="python /opt/airflow/scripts/extract_load.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test",
    )

    extract_load >> dbt_run >> dbt_test
