import os
import json
import logging

import boto3

PREDICTIONS_INPUT_STREAM: str = os.getenv('PREDICTIONS_INPUT_STREAM')
PREDICTIONS_OUTPUT_STREAM: str = os.getenv('PREDICTIONS_OUTPUT_STREAM')


class KinesisStream:
    def __init__(self, kinesis_client, name: str) -> None:
        self.kinesis_client = kinesis_client
        self.name = name

    def put_record(self, data):
        try:
            self.kinesis_client.put_record(
                StreamName=self.name, Data=json.dumps(data), PartitionKey='1'
            )

            logging.info('Put records in stream %s.', self.name)

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
    kinesis_client = boto3.client('kinesis')
    input_stream = KinesisStream(kinesis_client, name=PREDICTIONS_INPUT_STREAM)
    input_stream.put_record(data)

    kinesis_client = boto3.client('kinesis')
    output_stream = KinesisStream(kinesis_client, name=PREDICTIONS_OUTPUT_STREAM)
    record = output_stream.get_records(shard_id='shardId-000000000000')

    return record
