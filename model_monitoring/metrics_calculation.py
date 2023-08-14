import os
import time
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

import pytz
import mlflow
from prefect import flow, task
from sklearn.metrics import accuracy_score

from streaming.model import load_artifacts
from orchestration.common import params, load_data
from model_monitoring.evidently_report import EvidentlyReport
from model_monitoring.grafana_database import create_db, insert_into_table

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

SEND_TIMEOUT: int = 10

TRACKING_SERVER_HOST = os.getenv('MLFLOW_TRACKING_URI')
PORT = 5000

mlflow.set_tracking_uri(f'http://{TRACKING_SERVER_HOST}:{PORT}')


def load_model() -> Tuple:
    model, label_encoder, _ = load_artifacts()
    return model, label_encoder


def get_prediction(data, model, label_encoder):
    train_prediction = model.predict(data)
    return label_encoder.inverse_transform(train_prediction)


def get_data() -> Tuple:
    X_train, X_test, y_train, y_test = load_data(params['data']['preprocessed'])

    model, label_encoder = load_model()

    X_train['prediction'] = get_prediction(X_train, model, label_encoder)
    X_train[params['target']] = y_train

    X_test['prediction'] = get_prediction(X_test, model, label_encoder)
    X_test[params['target']] = y_test

    return X_train, X_test


@task(name='Creating and exporting report')
def get_metrics(train_data, test_data) -> Dict:
    evidentlyReport = EvidentlyReport(
        train_data,
        test_data,
        params['features']['numerical'],
        params['features']['categorical'],
        params['target'],
    )
    return evidentlyReport.get_metrics()


@task(name='Calculate accuracy metrics')
def calculate_accuracy_metrics(test_data) -> Tuple[List, List]:
    accuracy = accuracy_score(test_data['Target'], test_data['prediction'])
    time_pytz = datetime.now(pytz.timezone('America/Bogota'))
    return accuracy, time_pytz


@flow(name='Create Evidently report', log_prints=True)
def main():
    X_train, X_test = get_data()

    metrics = get_metrics(X_train, X_test)
    drift_detected = metrics[0]['result']['drift_detected']

    if drift_detected:
        pass

    metrics_dict = {
        'timestamp': [f"{datetime.now(pytz.timezone('America/Bogota'))}"],
        'column_drift_metric': [metrics[0]['result']['drift_score']],
        'number_of_drifted_columns': [metrics[1]['result']['number_of_drifted_columns']],
        'current_share_of_missing_values': [
            metrics[2]['result']['current']['share_of_missing_values']
        ],
        'reference_share_of_missing_values': [
            metrics[2]['result']['reference']['share_of_missing_values']
        ],
    }
    create_db()

    print('Reporting Evidently metrics')
    insert_into_table('evidently_metrics', metrics_dict)

    last_send = datetime.now() - timedelta(seconds=10)
    accuracy_list, timestamp_list = [], []
    for _ in range(10):
        print('Calculating accuracy metrics')
        accuracy, timestamp = calculate_accuracy_metrics(X_test)
        accuracy_list.append(accuracy)
        timestamp_list.append(timestamp)

        new_send = datetime.now()
        seconds_elapsed = (new_send - last_send).total_seconds()
        if seconds_elapsed < SEND_TIMEOUT:
            time.sleep(SEND_TIMEOUT - seconds_elapsed)
        while last_send < new_send:
            last_send += timedelta(seconds=10)

    accuracy_metrics = {'accuracy': accuracy_list, 'timestamp': timestamp_list}

    print('Reporting accuracy metrics')
    insert_into_table('accuracy_metrics', accuracy_metrics)
    logging.info('Data sent!')


if __name__ == '__main__':
    main()
