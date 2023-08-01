# pylint: disable= duplicate-code
import os
from typing import Dict, List

import mlflow

from orchestration.common import params, mlflow_experiment
from orchestration.args_mlflow_experiment import ArgsMLFlowExperiment

os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
MLFLOW_TRACKING_URI: str = os.getenv('MLFLOW_TRACKING_URI')
PORT: int = params['MLFLOW']['PORT']

mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')
mlflow.set_experiment(params['MLFLOW']['EXPERIMENTS'])


def run_pipeline(data_path, dict_features: Dict[str, List[str]]) -> None:
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

    args_mlflow_experiment = ArgsMLFlowExperiment(
        mlflow, hyperparams, data_path, dict_features
    )
    mlflow_experiment(args_mlflow_experiment)


if __name__ == '__main__':
    run_pipeline(params['DATA']['PREPROCESSED'], params['FEATURES'])
