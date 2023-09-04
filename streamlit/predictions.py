import os
import json
import logging

import boto3
import requests

PREDICTIONS_INPUT_STREAM: str = os.getenv('PREDICTIONS_INPUT_STREAM')
PREDICTIONS_OUTPUT_STREAM: str = os.getenv('PREDICTIONS_OUTPUT_STREAM')


class KinesisStream:
    def __init__(self, kinesis_client, name: str) -> None:
        self.kinesis_client = kinesis_client
        self.name = name

    def put_record(self, data):
        try:
            URL = 'http://backend:8080/2015-03-31/functions/function/invocations'
            data = {
                "Records": [
                    {
                        "kinesis": {
                            "data": "ewogICAgICAgICAgICAgICAgInN0dWRlbnRfZmVhdHVyZXMiIDogewogICAgICAgICAgICAgICAgICAgICAgICAiR0RQIjogMS43NCwKICAgICAgICAgICAgICAgICAgICAgICAgIkluZmxhdGlvbiByYXRlIjogMS40LAogICAgICAgICAgICAgICAgICAgICAgICAiVHVpdGlvbiBmZWVzIHVwIHRvIGRhdGUiOiAxLAogICAgICAgICAgICAgICAgICAgICAgICAiU2Nob2xhcnNoaXAgaG9sZGVyIjogMCwKICAgICAgICAgICAgICAgICAgICAgICAgIkN1cnJpY3VsYXIgdW5pdHMgMXN0IHNlbSAoYXBwcm92ZWQpIjogNSwKICAgICAgICAgICAgICAgICAgICAgICAgIkN1cnJpY3VsYXIgdW5pdHMgMXN0IHNlbSAoZW5yb2xsZWQpIjogNiwKICAgICAgICAgICAgICAgICAgICAgICAgIkN1cnJpY3VsYXIgdW5pdHMgMm5kIHNlbSAoYXBwcm92ZWQpIjogNQogICAgICAgICAgICAgICAgfSwKICAgICAgICAgICAgICAgICJzdHVkZW50X2lkIjogMjU2CiAgICAgICAgICAgICAgICB9"
                        }
                    }
                ]
            }
            requests.post(URL, json=data, timeout=200)
        except:
            logging.exception('Could not put record in stream %s.', self.name)
            raise

    def get_records(self, shard_id: str, shard_iterator_type: str = 'TRIM_HORIZON'):
        try:
            shard_iterator = self.kinesis_client.get_shard_iterator(
                StreamName=self.name,
                ShardId=shard_id,
                ShardIteratorType=shard_iterator_type,
            )

            result = self.kinesis_client.get_records(
                ShardIterator=shard_iterator['ShardIterator']
            )
            response = result['Records']

            response = json.loads(response[0]['Data'])

            logging.info('Get records from stream %s.', self.name)

            return response
        except:
            logging.exception('Could not get record from stream %s.', self.name)
            raise


def get_prediction(data: dict) -> str:
    # kinesis_client = boto3.client('kinesis', endpoint_url=endpoint_url)
    kinesis_input_stream = KinesisStream(None, name='')
    kinesis_input_stream.put_record(data)

    endpoint_url = 'http://kinesis:4566'
    kinesis_client = boto3.client('kinesis', endpoint_url=endpoint_url)
    kinesis_output_stream = KinesisStream(kinesis_client, name=PREDICTIONS_OUTPUT_STREAM)
    record = kinesis_output_stream.get_records(shard_id='shardId-000000000000')

    return record
