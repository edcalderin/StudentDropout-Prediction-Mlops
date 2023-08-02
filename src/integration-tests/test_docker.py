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
            'model': 'student-dropout-classifier',
            'version': 'd3c84a6e43d3476cb774b9b28a73b527',
            'prediction': {'output': 'Graduate', 'student_id': 256},
        }
    ]
}

diff = DeepDiff(response, expected, significant_digits=1)

print(f'{response=}')
print(f'{diff=}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff
