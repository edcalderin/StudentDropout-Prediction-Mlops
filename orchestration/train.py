# pylint: disable= duplicate-code
import os
import argparse
import warnings
from typing import Dict

import mlflow
from prefect import flow, task
from mlflow.tracking import MlflowClient

from orchestration.common import params, parse_param, mlflow_experiment
from orchestration.preprocess import preprocess
from orchestration.args_mlflow_experiment import ArgsMLFlowExperiment

warnings.filterwarnings('ignore')

os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
MLFLOW_TRACKING_URI: str = os.getenv('MLFLOW_TRACKING_URI')
PORT: int = params['MLFLOW']['PORT']

mlflow_client = MlflowClient(tracking_uri=f'http://{MLFLOW_TRACKING_URI}:{PORT}')


def get_best_params() -> Dict:
    experiment = mlflow_client.get_experiment_by_name(
        params['MLFLOW']['EXPERIMENTS']['OPTIMIZED_MODELS']
    )
    runs = mlflow_client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        order_by=['metrics.test_accuracy DESC'],
    )
    return runs[0].data.params


@task(name='Train model')
def train(data_path: str):
    print('Create a new run for the best model')
    mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')
    mlflow.set_experiment(params['MLFLOW']['EXPERIMENTS']['BEST_MODEL'])

    print('Getting the best params...')
    best_params = get_best_params()
    best_params = {key: parse_param(value) for key, value in best_params.items()}

    print('Training model...')
    args_mlflow_experiment = ArgsMLFlowExperiment(
        mlflow=mlflow,
        hyperparams=best_params,
        data_path=data_path,
        features=params['FEATURES'],
        log_artifacts=True,
    )

    mlflow_experiment(args_mlflow_experiment)


def get_best_model_uri():
    best_model_experiment_name = params['MLFLOW']['EXPERIMENTS']['BEST_MODEL']

    print(f'Getting experiment with name {best_model_experiment_name}')
    experiment = mlflow_client.get_experiment_by_name(best_model_experiment_name)

    runs = mlflow_client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        order_by=['created DESC'],
    )
    run_id: str = runs[0].info.run_id
    return f"runs:/{run_id}/model"


@task(name='Register model')
def register_model():
    print('Registering model...')

    model_uri = get_best_model_uri()
    model_name = params['MODEL_NAME']
    model_version = mlflow.register_model(model_uri=model_uri, name=model_name)

    mlflow_client.transition_model_version_stage(
        name=model_name,
        version=model_version.version,
        stage='staging',
        archive_existing_versions=True,
    )

    latest_versions = mlflow_client.get_latest_versions(name=model_name)
    for version in latest_versions:
        print(f"Version: {version.version}, stage: {version.current_stage}")


@flow(
    log_prints=True,
)
def train_flow(data_path: str) -> None:
    preprocess()
    train(data_path)
    register_model()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--data_path',
        default=params['DATA']['PREPROCESSED'],
        help='Location where the processed data was saved',
    )

    args = arg_parser.parse_args()
    train_flow(args.data_path)
