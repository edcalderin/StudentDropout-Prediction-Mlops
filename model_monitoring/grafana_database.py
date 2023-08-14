import os
from typing import Dict
from contextlib import contextmanager

import pandas as pd
import psycopg2
from prefect import task
from sqlalchemy import create_engine

GRAFANA_HOSTNAME = os.getenv('GRAFANA_HOSTNAME', 'localhost')
GRAFANA_DB_USER = os.getenv('GRAFANA_DB_USER', 'postgres')
GRAFANA_DB_PASSWORD = os.getenv('GRAFANA_DB_PASSWORD', 'mypass123')
GRAFANA_DB_NAME = os.getenv('GRAFANA_DB_NAME', 'student_dropout_grafana_db')
GRAFANA_DB_PORT = os.getenv('GRAFANA_DB_PORT', '5432')

psycopg_conn = f'postgresql://{GRAFANA_DB_USER}:{GRAFANA_DB_PASSWORD}@{GRAFANA_HOSTNAME}/{GRAFANA_DB_NAME}'


@contextmanager
def get_connection(exists_db: bool = True):
    CONNECTION_STRING: str = f'''
    host={GRAFANA_HOSTNAME}
    port={GRAFANA_DB_PORT}
    user={GRAFANA_DB_USER}
    password={GRAFANA_DB_PASSWORD}
    '''
    if exists_db:
        CONNECTION_STRING += f' dbname={GRAFANA_DB_NAME}'
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        conn.autocommit = True
        yield conn
    except psycopg2.OperationalError as e:
        print('Error connecting to PostgreSQL: ', e)
        conn.close()


@task(name='Create database')
def create_db() -> None:
    with get_connection(exists_db=False) as conn:
        cursor = conn.cursor()

        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{GRAFANA_DB_NAME}'")
        if len(cursor.fetchall()) == 0:
            cursor.execute(f"CREATE DATABASE {GRAFANA_DB_NAME};")


def insert_into_table(table_name: str, data: Dict) -> None:
    engine = create_engine(psycopg_conn)
    dataframe = pd.DataFrame(data)
    dataframe.to_sql(table_name, engine, if_exists='append', index=False)
