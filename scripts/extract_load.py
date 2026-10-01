import os
import pandas as pd
from sqlalchemy import create_engine, text

# Connection info comes from environment variables set in docker-compose.yml
DW_HOST = os.environ.get("DW_HOST", "localhost")
DW_PORT = os.environ.get("DW_PORT", "5432")
DW_DB = os.environ.get("DW_DB", "datawarehouse")
DW_USER = os.environ.get("DW_USER", "dwuser")
DW_PASSWORD = os.environ.get("DW_PASSWORD", "dwpass")

DATA_DIR = os.environ.get("DATA_DIR", "/opt/airflow/data")

# Maps: raw table name -> source CSV file name
TABLES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def get_engine():
    url = f"postgresql+psycopg2://{DW_USER}:{DW_PASSWORD}@{DW_HOST}:{DW_PORT}/{DW_DB}"
    return create_engine(url)


def load_table(engine, table_name: str, csv_file: str):
    csv_path = os.path.join(DATA_DIR, csv_file)
    print(f"Reading {csv_path} ...")
    df = pd.read_csv(csv_path)

    # Drop the table with CASCADE first: dbt views/tables downstream may depend
    # on it from a previous run, and plain to_sql(if_exists="replace") cannot
    # drop a table that has dependents.
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS raw.{table_name} CASCADE"))

    print(f"Loading {len(df)} rows into raw.{table_name} ...")
    df.to_sql(
        table_name,
        engine,
        schema="raw",
        if_exists="append",  # table was just dropped above, so append = fresh create
        index=False,
        chunksize=5000,
    )
    print(f"Done: raw.{table_name}")


def main():
    engine = get_engine()

    # Make sure the raw schema exists before loading into it
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))

    for table_name, csv_file in TABLES.items():
        load_table(engine, table_name, csv_file)

    print("Extract & Load step finished successfully.")


if __name__ == "__main__":
    main()