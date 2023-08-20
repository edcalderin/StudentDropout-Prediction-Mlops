# pylint: disable= duplicate-code

import os
from typing import Dict
from datetime import datetime

import pytz
import pandas as pd
from sqlalchemy import create_engine
from evidently_report import EvidentlyReport

from orchestration.common import params

GRAFANA_HOSTNAME = os.getenv('GRAFANA_HOSTNAME', 'db')
GRAFANA_DB_USER = os.getenv('GRAFANA_DB_USER')
GRAFANA_DB_PASSWORD = os.getenv('GRAFANA_DB_PASSWORD')
GRAFANA_DB_NAME = os.getenv('GRAFANA_DB_NAME')
GRAFANA_DB_PORT = os.getenv('GRAFANA_DB_PORT', '5432')

psycopg_conn = f'postgresql://{GRAFANA_DB_USER}:{GRAFANA_DB_PASSWORD}@{GRAFANA_HOSTNAME}/{GRAFANA_DB_NAME}'


class GrafanaCallback:
    def __init__(self, table_name: str = 'evidently_metrics') -> None:
        self.table_name = table_name

    def insert_into_table(self, data: Dict) -> None:
        engine = create_engine(psycopg_conn)
        dataframe = pd.DataFrame(data, index=[0])
        dataframe.to_sql(self.table_name, engine, if_exists='append', index=False)

    def get_metrics(self, current_data: pd.DataFrame) -> Dict:
        evidentlyReport = EvidentlyReport(
            numerical_features=params['features']['numerical'],
            categorical_features=params['features']['categorical'],
        )
        return evidentlyReport.get_metrics(current_data)

    def report_metrics(self, features, prediction):
        current_data = features | {'prediction': prediction['prediction']['output']}
        current_data = pd.DataFrame(current_data, index=[0])
        metrics = self.get_metrics(current_data)

        drift_detected = metrics[0]['result']['drift_detected']
        if drift_detected:
            print('ATENTION: Drift detected!!! Retrain the model')

        metrics_dict = {
            'timestamp': [f"{datetime.now(pytz.timezone('America/Bogota'))}"],
            'column_drift_metric': [metrics[0]['result']['drift_score']],
            'number_of_drifted_columns': [
                metrics[1]['result']['number_of_drifted_columns']
            ],
            'current_share_of_missing_values': [
                metrics[2]['result']['current']['share_of_missing_values']
            ],
            'reference_share_of_missing_values': [
                metrics[2]['result']['reference']['share_of_missing_values']
            ],
        }

        self.insert_into_table(metrics_dict)
