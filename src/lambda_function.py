import os

import mlflow

import model

os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
PREDICTIONS_OUTPUT_STREAM = os.getenv('PREDICTIONS_OUTPUT_STREAM')
TRACKING_SERVER_HOST = os.getenv('MLFLOW_TRACKING_URI')
TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'
PORT = 5000

mlflow.set_tracking_uri(f'http://{TRACKING_SERVER_HOST}:{PORT}')
print(mlflow.get_tracking_uri())
model_service = model.init(PREDICTIONS_OUTPUT_STREAM, TEST_RUN)


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    return model_service.lambda_handler(event)
