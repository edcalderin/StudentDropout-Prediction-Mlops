import os

import mlflow

from src import model, params

PREDICTIONS_OUTPUT_STREAM = os.getenv('PREDICTIONS_OUTPUT_STREAM')
TRACKING_SERVER_HOST = os.getenv('MLFLOW_TRACKING_URI')
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'
PORT = params['MLFLOW']['PORT']
mlflow.set_tracking_uri(f'http://{TRACKING_SERVER_HOST}:{PORT}')

model_service = model.init(PREDICTIONS_OUTPUT_STREAM, TEST_RUN)


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    return model_service.lambda_handler(event)
