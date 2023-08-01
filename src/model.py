import os
import json
import base64
import pickle
from typing import Tuple
from pathlib import Path

import boto3
import mlflow
import pandas as pd

from src import params


def get_model_location() -> str:
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    stage = os.getenv('STAGE', 'Staging')

    return f"models:/{params['MODEL_NAME']}/{stage}"


def download_artifacts(run_id: str) -> str:
    encoder_location = os.getenv('ENCODER_LOCATION')

    # If path does not exist, then it is MLFlow Artifact uri and will be downloaded and replace
    # the remote location with the local filesystem one
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
    def __init__(self, model, label_encoder, run_id, callbacks=None) -> None:
        self.model = model
        self.label_encoder = label_encoder
        self.run_id = run_id
        self.callbacks = callbacks or []

    def predict(self, features) -> str:
        df = pd.DataFrame(features, index=[0])
        prediction = self.model.predict(df)
        prediction = self.label_encoder.inverse_transform(prediction)
        return list(prediction)

    def lambda_handler(self, event):
        predictions = []
        print(json.dumps(event))
        for record in event['Records']:
            encoded_data = record['kinesis']['data']

            student_event = base64_decode(encoded_data)

            student_features, student_id = (
                student_event['student_features'],
                student_event['student_id'],
            )

            prediction = self.predict(student_features)

            prediction_event = {
                'model': params['MODEL_NAME'],
                'version': self.run_id,
                'prediction': {
                    'output': prediction,
                    'student_id': student_id,
                },
            }
            print(f'{prediction_event=}')
            for callback in self.callbacks:
                callback(prediction_event)

            predictions.append(prediction_event)

        return {'predictions': predictions}


class KinesisCallback:
    def __init__(self, kinesis_client, prediction_output_stream: str) -> None:
        self.kinesis_client = kinesis_client
        self.prediction_output_stream = prediction_output_stream

    def put_record(self, prediction_event) -> None:
        self.kinesis_client.put_record(
            StreamName=self.prediction_output_stream,
            Data=json.dumps(prediction_event),
            PartitionKey='1',
        )


def create_kinesis_client():
    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')
    print(f'{endpoint_url=}')

    if endpoint_url is None:
        return boto3.client('kinesis')
    return boto3.client('kinesis', endpoint_url=endpoint_url)


def init(prediction_output_stream, test_run: bool):
    model, label_encoder, run_id = load_artifacts()

    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()

        kinesis_callback = KinesisCallback(kinesis_client, prediction_output_stream)
        callbacks.append(kinesis_callback.put_record)

    return ModelService(model, label_encoder, run_id, callbacks)


def base64_decode(encoded_data: str):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    return json.loads(decoded_data)
