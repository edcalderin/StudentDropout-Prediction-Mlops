
import mlflow
import os
from typing import List, Dict
from common import load_data, params, mlflow_experiment

os.environ['MLFLOW_TRACKING_URI'] = 'ec2-18-217-232-157.us-east-2.compute.amazonaws.com'
os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
MLFLOW_TRACKING_URI:str = os.getenv('MLFLOW_TRACKING_URI')
PORT: int=params['MLFLOW_PORT']

mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')
mlflow.set_experiment('student-dropout-models')

def run_pipeline(data, dict_features:Dict[str, List[str]])-> None:
    # Random params
    hyper_params = {
       'colsample_bylevel': 1,
       'learning_rate': 0.002,
       'max_depth': 35,
       'min_child_weight': 1,
       'n_estimators': 300,
       'n_jobs': -1,
       'eval_metric': 'logloss',
       'random_state': 42,
       'objective': 'binary:logistic'
    }

    mlflow_experiment(mlflow, hyper_params, data, dict_features)

def train():

    data = load_data(params['DATA']['PREPROCESSED'])

    run_pipeline(data, params['FEATURES'])

if __name__=='__main__':
    train()