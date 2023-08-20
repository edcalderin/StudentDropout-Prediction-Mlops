import os
import json
import base64
import pickle
import multiprocessing
from typing import Tuple
from pathlib import Path

import boto3
import mlflow
import pandas as pd
from grafana_manager import GrafanaCallback

MODEL_NAME = os.getenv('MODEL_NAME', 'student-dropout-classifier')


def get_model_location() -> str:
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    stage = os.getenv('STAGE', 'Staging')
    return f"models:/{MODEL_NAME}/{stage}"


def download_artifacts(run_id: str):
    encoder_location = os.getenv('ENCODER_LOCATION')

    if encoder_location is not None:
        return encoder_location

    encoder_location = f'runs:/{run_id}/encoders/'
    encoder_location = mlflow.artifacts.download_artifacts(encoder_location)
    return encoder_location


def load_artifacts() -> Tuple:
    model_location = get_model_location()
    model = mlflow.pyfunc.load_model(model_location)
    run_id = model.metadata.get_model_info().run_id
    encoder_location = download_artifacts(run_id)
    with open(Path(encoder_location) / 'label_encoder.pkl', 'rb') as file:
        label_encoder = pickle.load(file)

    return model, label_encoder, run_id


class ModelService:
    def __init__(self, artifacts, put_record=None, report_metrics=None) -> None:
        self.artifacts = artifacts
        self.put_record = put_record or None
        self.report_metrics = report_metrics or None

    def predict(self, features) -> str:
        df = pd.DataFrame(features, index=[0])
        model, label_encoder, _ = self.artifacts
        prediction = model.predict(df)
        prediction = label_encoder.inverse_transform(prediction)
        return prediction[0]

    def lambda_handler(self, event):
        predictions = []
        *_, run_id = self.artifacts
        for record in event['Records']:
            encoded_data = record['kinesis']['data']

            student_event = base64_decode(encoded_data)
            student_features, student_id = (
                student_event['student_features'],
                student_event['student_id'],
            )

            prediction = self.predict(student_features)

            prediction_event = {
                'model': MODEL_NAME,
                'version': run_id,
                'prediction': {
                    'output': prediction,
                    'student_id': student_id,
                },
            }

            if self.put_record is not None and self.report_metrics is not None:
                background_process = multiprocessing.Process(
                    target=self.report_metrics, args=(student_features, prediction_event)
                )
                background_process.start()

                self.put_record(prediction_event)
                background_process.join()

            predictions.append(prediction_event)

        return {'predictions': predictions}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_output_stream: str) -> None:
        self.kinesis_client = kinesis_client
        self.prediction_output_stream = prediction_output_stream

    def put_record(self, prediction_event) -> None:
        # pylint: disable=unused-argument

        self.kinesis_client.put_record(
            StreamName=self.prediction_output_stream,
            Data=json.dumps(prediction_event),
            PartitionKey='1',
        )


def create_kinesis_client():
    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')

    if endpoint_url is None:
        return boto3.client('kinesis')
    print(f'{endpoint_url=}')
    return boto3.client('kinesis', endpoint_url=endpoint_url)


def init(prediction_output_stream, test_run: bool):
    artifacts = load_artifacts()

    put_record_callback, report_metrics_callback = None, None

    if not test_run:
        kinesis_client = create_kinesis_client()

        kinesis_callback = KinesisCallback(kinesis_client, prediction_output_stream)
        grafana_callback = GrafanaCallback()
        put_record_callback = kinesis_callback.put_record
        report_metrics_callback = grafana_callback.report_metrics

    return ModelService(artifacts, put_record_callback, report_metrics_callback)


def base64_decode(encoded_data: str):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    return json.loads(decoded_data)
