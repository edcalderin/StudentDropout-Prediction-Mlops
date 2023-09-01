# pylint: disable= duplicate-code

import os
from typing import Dict
from datetime import datetime

import pytz
import pandas as pd
from sqlalchemy import create_engine
from evidently_report import EvidentlyReport

from config.params import params

POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME', 'db')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

psycopg_conn = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}'


class GrafanaCallback:
    def insert_into_table(self, table_name, data: Dict) -> None:
        engine = create_engine(psycopg_conn)

        # Attaching timezone column to incoming data dictionary
        timestamp = f"{datetime.now(pytz.timezone('America/Bogota'))}"
        data_copy = data.copy() | {'timezone': timestamp}

        dataframe = pd.DataFrame(data_copy, index=[0])
        dataframe.to_sql(table_name, engine, if_exists='append', index=False)

    def get_metrics(
        self, train_dataset: pd.DataFrame, current_data: pd.DataFrame
    ) -> Dict:
        evidentlyReport = EvidentlyReport(
            numerical_features=params['features']['numerical'],
            categorical_features=params['features']['categorical'],
        )

        metrics = evidentlyReport.get_evidently_metrics(train_dataset, current_data)

        metrics_dict = {
            'drift_detected': metrics[0]['result']['drift_detected'],
            'column_drift_metric': metrics[0]['result']['drift_score'],
            'number_of_drifted_columns': metrics[1]['result'][
                'number_of_drifted_columns'
            ],
            'current_share_of_missing_values': metrics[2]['result']['current'][
                'share_of_missing_values'
            ],
            'reference_share_of_missing_values': metrics[2]['result']['reference'][
                'share_of_missing_values'
            ],
        }

        return metrics_dict

    def report_metrics(
        self, train_dataset: pd.DataFrame, features: Dict, prediction: Dict
    ):
        current_data = features | {'prediction': prediction['prediction']['output']}

        # Persist incoming data points into db
        self.insert_into_table('historical_data', current_data)

        # Calculate Evidently metrics with the incoming data
        metrics = self.get_metrics(train_dataset, pd.DataFrame(current_data, index=[0]))

        # Send alert if drift is detected
        if metrics['drift_detected']:
            print('ATENTION: Drift detected!!!')

        self.insert_into_table('evidently_metrics', metrics)
