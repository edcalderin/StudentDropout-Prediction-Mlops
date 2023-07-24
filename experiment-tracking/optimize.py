import optuna
from utils import load_data, params, mlflow_experiment
import mlflow
import os
from typing import Dict, List

os.environ['MLFLOW_TRACKING_URI'] = 'ec2-18-217-232-157.us-east-2.compute.amazonaws.com'
os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
MLFLOW_TRACKING_URI:str = os.getenv('MLFLOW_TRACKING_URI')
PORT: int=params['MLFLOW_PORT']

mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')
mlflow.set_experiment('optimized-student-dropout-models')

def objective(trial: optuna.Trial, data, features: Dict[str, List[str]]):
    hyper_params = {
        'n_estimators': trial.suggest_int('n_estimators', 500, 5000, step=100),
        'learning_rate': trial.suggest_float('learning_rate', 1e-4, 0.1, log=True),
        'max_depth': trial.suggest_int('max_depth', 30, 120),
        'subsample': trial.suggest_float('subsample', 0.5, 1, step=0.1),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1, step=0.1),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'gamma': trial.suggest_float('gamma', 0, 0.5, step=0.1),
        'eval_metric': 'logloss',
        'objective': 'binary:logistic',
        'random_state': 42,
        'n_jobs': -1,
        'tree_method':'gpu_hist'
    }

    return mlflow_experiment(mlflow, hyper_params, data, features)

def run(n_trials: int):
    study = optuna.create_study(direction='maximize')

    data = load_data(params['DATA']['PREPROCESSED'])
    objective_func = lambda trial: objective(trial, data, params['FEATURES'])

    study.optimize(objective_func, n_trials=n_trials)

    print(f'Test accuracy optimzed: {study.best_value}')
    print(f'Best params: {study.best_params}')

run(70)
