import os
import mlflow
from typing import Dict, Any
import pickle
import pandas as pd

os.environ['MLFLOW_TRACKING_URI'] = 'ec2-18-217-232-157.us-east-2.compute.amazonaws.com'
os.environ['AWS_PROFILE'] = 'student-dropout-classifier'
MLFLOW_TRACKING_URI:str = os.getenv('MLFLOW_TRACKING_URI')
RUN_ID: str = os.getenv('RUN_ID')
PORT: int=5000

mlflow.set_tracking_uri(f'http://{MLFLOW_TRACKING_URI}:{PORT}')

def get_model_location() -> str:
    model_location = os.getenv('MODEL_LOCATION')
    if model_location is not None:
        return model_location

    model_name = os.getenv('MODEL_NAME', 'student-dropout-classifier')
    stage = os.getenv('STAGE', 'Staging')
    logged_model = f'models:/{model_name}/{stage}'
    logged_artifact = f'runs:/{RUN_ID}/encoders/'
    return logged_model, logged_artifact

def load_artifacts():
    logged_model, logged_artifact = get_model_location()

    label_encoder = mlflow.artifacts.download_artifacts(logged_artifact, dst_path='artifacts/encoders')
    with open('encoders/label_encoder.pkl', 'rb') as file:
        label_encoder = pickle.load(file)

    model = mlflow.pyfunc.load_model(logged_model)
    return model, label_encoder

def predict(features: Dict[str, Any])-> str:
    model, label_encoder = load_artifacts()
    df = pd.DataFrame(features, index=[0])
    prediction = model.predict(df)
    prediction = label_encoder.inverse_transform(prediction)
    return prediction

features = {
        'GDP': 1.74,
        'Inflation rate': 1.4,
        'Tuition fees up to date': 1,
        'Scholarship holder': 0,
        'Curricular units 1st sem (approved)': 5,
        'Curricular units 1st sem (enrolled)': 6,
        'Curricular units 2nd sem (approved)': 5
    }

print(predict(features))

