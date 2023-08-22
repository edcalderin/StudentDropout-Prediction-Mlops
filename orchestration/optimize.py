# pylint: disable=import-error
import os
import argparse
import warnings
from typing import Dict

import mlflow
import optuna
from common import mlflow_experiment

from config.params import params

warnings.filterwarnings('ignore')

MLFLOW_TRACKING_URI: str = os.getenv('MLFLOW_TRACKING_URI')


def objective(trial: optuna.Trial, config: Dict):
    PORT: int = config['mlflow']['port']

    mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')

    mlflow.set_experiment(config['mlflow']['experiments']['optimized_models'])

    hyperparams = {
        'n_estimators': trial.suggest_int('n_estimators', 800, 4000, step=100),
        'learning_rate': trial.suggest_float('learning_rate', 1e-4, 0.1, log=True),
        'max_depth': trial.suggest_int('max_depth', 40, 100),
        'subsample': trial.suggest_float('subsample', 0.5, 1, step=0.1),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1, step=0.1),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 7),
        'gamma': trial.suggest_float('gamma', 0, 0.4, step=0.1),
        'eval_metric': 'logloss',
        'objective': 'binary:logistic',
        'random_state': 42,
        'n_jobs': -1,
        'tree_method': 'gpu_hist',
    }

    return mlflow_experiment(mlflow, hyperparams, config['features'])


def run(n_trials: int, config: Dict):
    # pylint: disable=unnecessary-lambda-assignment

    study = optuna.create_study(direction='maximize')

    objective_func = lambda trial: objective(trial, config)

    study.optimize(objective_func, n_trials=n_trials)

    print(f'Test accuracy optimzed: {study.best_value}')
    print(f'Best params: {study.best_params}')


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--num_trials', default=50, type=int, help='Number of trials for the optimizer'
    )

    args = arg_parser.parse_args()

    run(args.num_trials, params)


if __name__ == '__main__':
    main()
