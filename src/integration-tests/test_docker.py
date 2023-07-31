# pylint: disable= duplicate-code
import json

import requests
from deepdiff import DeepDiff

with open('event.json', 'rt', encoding='utf-8') as file:
    event = json.load(file)

URL = 'http://localhost:8080/2015-03-31/functions/function/invocations'
response = requests.post(URL, json=event, timeout=100).json()

expected = {
    'predictions': [
        {
            'model': 'ride_duration_prediction_model',
            'version': 'RUN_ID',
            'prediction': {
                'ride_duration': 20.002716357802516,
                'ride_id': 5,
            },
        }
    ]
}

diff = DeepDiff(response, expected, significant_digits=1)

print(f'{response=}')
print(f'{diff=}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff
