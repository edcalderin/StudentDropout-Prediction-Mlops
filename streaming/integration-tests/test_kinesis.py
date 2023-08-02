# pylint: disable= duplicate-code
import os
import json

import boto3
from deepdiff import DeepDiff

kinesis_stream_name = os.getenv(
    'PREDICTIONS_OUTPUT_STREAM', 'student-dropout-output-stream'
)
kinesis_endpoint = os.getenv('KINESIS_ENDPOINT_URL', 'http://localhost:4566')

kinesis_client = boto3.client('kinesis', endpoint_url=kinesis_endpoint)

SHARD_ID = 'shardId-000000000000'

shard_iterator = kinesis_client.get_shard_iterator(
    StreamName=kinesis_stream_name,
    ShardId=SHARD_ID,
    ShardIteratorType='TRIM_HORIZON',
)

result = kinesis_client.get_records(ShardIterator=shard_iterator['ShardIterator'])

response = result['Records']

assert len(response) == 1, 'Lenght does not match'

response = json.loads(response[0]['Data'])

expected = {
    'model': 'student-dropout-classifier',
    'version': 'd3c84a6e43d3476cb774b9b28a73b527',
    'prediction': {'output': 'Graduate', 'student_id': 256},
}

diff = DeepDiff(response, expected, significant_digits=1)

print(f'{response=}')
print(f'{diff=}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff
