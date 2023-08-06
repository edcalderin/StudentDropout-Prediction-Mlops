import os
import time
import random
import logging
from datetime import datetime, timedelta
from contextlib import contextmanager

import pytz
import psycopg
from psycopg import Cursor

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

SEND_TIMEOUT: int = 10

rand = random.Random()
GRAFANA_HOSTNAME = os.getenv('GRAFANA_HOSTNAME', 'localhost')
GRAFANA_DB_USER = os.getenv('GRAFANA_DB_USER', 'postgres')
GRAFANA_DB_PASSWORD = os.getenv('GRAFANA_DB_PASSWORD', 'mypass123')
GRAFANA_DB_NAME = os.getenv('GRAFANA_DB_NAME', 'student_dropout_grafana_db')
GRAFANA_DB_PORT = os.getenv('GRAFANA_DB_PORT', '5432')


@contextmanager
def get_connection():
    CONNECTION_STRING = f'host={GRAFANA_HOSTNAME} port={GRAFANA_DB_PORT} user={GRAFANA_DB_USER} password={GRAFANA_DB_PASSWORD}'
    try:
        conn = psycopg.connect(CONNECTION_STRING, autocommit=True)
        yield conn
    except psycopg.OperationalError as e:
        print('Error connecting to PostgreSQL: ', e)
        conn.close()


def create_db():
    with get_connection() as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{GRAFANA_DB_NAME}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"CREATE DATABASE {GRAFANA_DB_NAME};")


def create_table():
    with get_connection() as conn:
        TABLE_NAME: str = 'metrics'
        QUERY = f'''
        DROP TABLE IF EXISTS {TABLE_NAME};
        CREATE TABLE {TABLE_NAME}(
            timestamp TIMESTAMP,
            accuracy FLOAT
        )
        '''
        conn.execute(QUERY)


def calculate_metrics_postgresql(curr: Cursor):
    accuracy = 0.925
    time_pytz = datetime.now(pytz.timezone('America/Bogota'))
    QUERY = f"INSERT INTO metrics(timestamp, accuracy) VALUES ('{time_pytz}', {accuracy})"

    curr.execute(QUERY)


def main():
    create_db()
    create_table()

    last_send = datetime.now() - timedelta(seconds=10)
    with get_connection() as conn:
        for _ in range(100):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr)
            new_send = datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send += timedelta(seconds=10)
            logging.info('Data sent!')


if __name__ == '__main__':
    main()
