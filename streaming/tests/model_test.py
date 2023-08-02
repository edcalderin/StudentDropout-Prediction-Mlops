from pathlib import Path

import model


def read_text(file: Path) -> str:
    test_directory = Path(__file__).parent

    with open(test_directory / file, 'rt', encoding='utf-8') as in_f:
        return in_f.read().strip()


def test_base64_decode(feature_fixture):
    base64 = read_text('data.b64')
    output = model.base64_decode(base64)
    expected_value = {'student_features': feature_fixture, 'student_id': 256}

    assert output == expected_value


class ModelMock:
    def __init__(self, value) -> None:
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


class LabelEncoderMock:
    def __init__(self, label) -> None:
        self.label = label

    def inverse_transform(self, prediction):
        n = len(prediction)
        return [self.label] * n


def test_predict(feature_fixture):
    features = [feature_fixture]
    model_mock = ModelMock(1)
    label_encoder_mock = LabelEncoderMock('Dropout')
    model_service = model.ModelService(model_mock, label_encoder_mock, '')
    predictions = model_service.predict(features)
    assert predictions == 'Dropout'


def test_lambda_handler():
    EVENT = {
        "Records": [
            {
                "kinesis": {
                    "data": read_text('data.b64'),
                }
            }
        ]
    }
    RUN_ID: str = '123'
    expected = {
        'predictions': [
            {
                'model': 'student-dropout-classifier',
                'version': RUN_ID,
                'prediction': {
                    'output': 'Graduate',
                    'student_id': 256,
                },
            }
        ]
    }

    model_mock = ModelMock(1)
    label_encoder_mock = LabelEncoderMock('Graduate')
    model_service = model.ModelService(model_mock, label_encoder_mock, RUN_ID)
    output = model_service.lambda_handler(EVENT)
    print(output)
    assert output == expected
