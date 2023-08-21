# pylint: disable= duplicate-code
import os

import mlflow

from config.params import params
from orchestration.common import mlflow_experiment

MLFLOW_TRACKING_URI: str = os.getenv('MLFLOW_TRACKING_URI')


def run_pipeline() -> None:
    PORT: int = params['mlflow']['port']

    mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')

    mlflow.set_experiment(params['mlflow']['experiments'])

    # Random params
    hyperparams = {
        'colsample_bylevel': 1,
        'learning_rate': 0.002,
        'max_depth': 35,
        'min_child_weight': 1,
        'n_estimators': 300,
        'n_jobs': -1,
        'eval_metric': 'logloss',
        'random_state': 42,
        'objective': 'binary:logistic',
    }

    mlflow_experiment(mlflow, hyperparams, params)


if __name__ == '__main__':
    run_pipeline()
