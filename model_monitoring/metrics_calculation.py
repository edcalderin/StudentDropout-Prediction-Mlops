import os
import time
import logging
from typing import Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager

import pytz
import mlflow
import psycopg
from prefect import flow, task
from psycopg import Cursor
from sklearn.metrics import accuracy_score

from streaming.model import load_artifacts
from orchestration.common import params, load_data
from model_monitoring.evidently_report import EvidentlyReport

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

SEND_TIMEOUT: int = 10

GRAFANA_HOSTNAME = os.getenv('GRAFANA_HOSTNAME', 'localhost')
GRAFANA_DB_USER = os.getenv('GRAFANA_DB_USER', 'postgres')
GRAFANA_DB_PASSWORD = os.getenv('GRAFANA_DB_PASSWORD', 'mypass123')
GRAFANA_DB_NAME = os.getenv('GRAFANA_DB_NAME', 'student_dropout_grafana_db')
GRAFANA_DB_PORT = os.getenv('GRAFANA_DB_PORT', '5432')
TRACKING_SERVER_HOST = os.getenv('MLFLOW_TRACKING_URI')
PORT = 5000

mlflow.set_tracking_uri(f'http://{TRACKING_SERVER_HOST}:{PORT}')


@contextmanager
def get_connection(exists_db: bool = True):
    CONNECTION_STRING = f'host={GRAFANA_HOSTNAME} port={GRAFANA_DB_PORT} user={GRAFANA_DB_USER} password={GRAFANA_DB_PASSWORD}'
    if exists_db:
        CONNECTION_STRING += f' dbname={GRAFANA_DB_NAME}'
    try:
        conn = psycopg.connect(CONNECTION_STRING, autocommit=True)
        yield conn
    except psycopg.OperationalError as e:
        print('Error connecting to PostgreSQL: ', e)
        conn.close()


def load_model() -> Tuple:
    model, label_encoder, _ = load_artifacts()
    return model, label_encoder


@task(name='Create database')
def create_db():
    with get_connection(exists_db=False) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{GRAFANA_DB_NAME}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"CREATE DATABASE {GRAFANA_DB_NAME};")


@task(name='Create table')
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


@task(name='Calculate metrics PostgreSQL')
def calculate_metrics_postgresql(curr: Cursor, test_data):
    accuracy = accuracy_score(test_data['Target'], test_data['prediction'])
    time_pytz = datetime.now(pytz.timezone('America/Bogota'))
    QUERY = f"INSERT INTO metrics(timestamp, accuracy) VALUES ('{time_pytz}', {accuracy})"

    curr.execute(QUERY)


def get_prediction(data, model, label_encoder):
    train_prediction = model.predict(data)
    return label_encoder.inverse_transform(train_prediction)


def get_data() -> Tuple:
    X_train, X_test, y_train, y_test = load_data(params['DATA']['PREPROCESSED'])

    model, label_encoder = load_model()

    X_train['prediction'] = get_prediction(X_train, model, label_encoder)
    X_train[params['TARGET']] = y_train

    X_test['prediction'] = get_prediction(X_test, model, label_encoder)
    X_test[params['TARGET']] = y_test

    return X_train, X_test


@task(name='Creating and exporting report')
def create_report(train_data, test_data):
    evidentlyReport = EvidentlyReport(
        train_data,
        test_data,
        params['FEATURES']['NUMERICAL'],
        params['FEATURES']['CATEGORICAL'],
        params['TARGET'],
    )
    evidentlyReport.create_report('./reports/evidently_report.html')


@flow(name='Create Evidently report', log_prints=True)
def main():
    X_train, X_test = get_data()

    create_report(X_train, X_test)

    create_db()
    create_table()

    last_send = datetime.now() - timedelta(seconds=10)
    with get_connection() as conn:
        for _ in range(50):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(curr, X_test)
            new_send = datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send += timedelta(seconds=10)
            logging.info('Data sent!')


if __name__ == '__main__':
    main()
