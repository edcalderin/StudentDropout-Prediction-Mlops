# pylint: disable= duplicate-code
import os
import warnings
from typing import Dict

import mlflow
from prefect import flow, task
from mlflow.tracking import MlflowClient

from config.params import params
from orchestration.common import parse_param, mlflow_experiment
from orchestration.preprocess import preprocess

warnings.filterwarnings('ignore')

MLFLOW_TRACKING_URI: str = os.getenv('MLFLOW_TRACKING_URI')


def get_best_params(mlflow_client, config: Dict) -> Dict:
    experiment = mlflow_client.get_experiment_by_name(
        config['mlflow']['experiments']['optimized_models']
    )
    runs = mlflow_client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=1,
        order_by=['metrics.test_accuracy DESC'],
    )
    return runs[0].data.params


@task(name='Train model')
def train(mlflow_client, config: Dict):
    print('Create a new run for the best model')
    mlflow.set_tracking_uri(f"http://{MLFLOW_TRACKING_URI}:{config['mlflow']['port']}")
    mlflow.set_experiment(config['mlflow']['experiments']['best_model'])

    print('Getting the best params...')
    best_params = get_best_params(mlflow_client, config)
    best_params = {key: parse_param(value) for key, value in best_params.items()}

    print('Training model...')
    mlflow_experiment(
        mlflow=mlflow, hyperparams=best_params, config=config, log_artifacts=True
    )


def get_best_model_uri(mlflow_client, config: Dict):
    best_model_experiment_name = config['mlflow']['experiments']['best_model']

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
def register_model(mlflow_client, config: Dict):
    print('Registering model...')

    model_uri = get_best_model_uri(mlflow_client, config)
    model_name = config['model_name']
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


@flow(name='Training', log_prints=True)
def train_flow() -> None:
    mlflow_client = MlflowClient(
        tracking_uri=f"http://{MLFLOW_TRACKING_URI}:{params['mlflow']['port']}"
    )

    preprocess()
    train(mlflow_client, params)
    register_model(mlflow_client, params)


if __name__ == '__main__':
    train_flow()
