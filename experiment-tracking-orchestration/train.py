import argparse
import mlflow
from mlflow.tracking import MlflowClient
from prefect import task, flow, get_run_logger
import os
from common import params, mlflow_experiment, parse_param
from typing import Dict
import warnings
warnings.filterwarnings('ignore')

os.environ['MLFLOW_TRACKING_URI'] = 'ec2-18-217-232-157.us-east-2.compute.amazonaws.com'
os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
MLFLOW_TRACKING_URI:str = os.getenv('MLFLOW_TRACKING_URI')
PORT: int=params['MLFLOW']['PORT']

mlflow_client = MlflowClient(tracking_uri=f'http://{MLFLOW_TRACKING_URI}:{PORT}')

def get_best_params()->Dict:
    experiment = mlflow_client.get_experiment_by_name(params['MLFLOW']['EXPERIMENTS']['OPTIMIZED_MODELS'])
    runs = mlflow_client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        order_by=['metrics.test_accuracy DESC']
    )
    return runs[0].data.params

@task(name='Train model')
def train(data_path:str):
    print('Create a new run for the best model')
    mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')
    mlflow.set_experiment(params['MLFLOW']['EXPERIMENTS']['BEST_MODEL'])

    print('Getting the best params...')
    best_params = get_best_params()
    best_params = {key: parse_param(value) for key, value in best_params.items()}

    print('Training model...')
    mlflow_experiment(
        mlflow=mlflow,
        hyper_params=best_params, 
        data_path=data_path, 
        features=params['FEATURES'],
        log_artifacts=True)

@task(name='Register model')
def register_model():
    best_model_experiment_name = params['MLFLOW']['EXPERIMENTS']['BEST_MODEL']
    
    print(f'Getting experiment with name {best_model_experiment_name}')
    experiment = mlflow_client.get_experiment_by_name(best_model_experiment_name)
    
    runs = mlflow_client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        order_by=['created DESC']
    )
    print('Registering model...')
    print(runs[0])

@flow(log_prints=True)
def train_pipeline(data_path: str)->None:
    train(data_path)
    register_model()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--data_path',
        default=params['DATA']['PREPROCESSED'],
        help='Location where the processed data was saved'
    )

    args = arg_parser.parse_args()
    train_pipeline(args.data_path)