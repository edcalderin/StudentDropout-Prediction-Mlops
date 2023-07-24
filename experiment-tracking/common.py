import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from feature_engine.encoding import RareLabelEncoder, CountFrequencyEncoder
from feature_engine.creation import MathFeatures
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pickle

def get_params():
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path) as file:
        return yaml.load(file, Loader=SafeLoader)

def metrics(model: Pipeline, X: pd.DataFrame, y_true: pd.Series)-> Dict[str, Any]:
    y_pred = model.predict(X)
    cm = confusion_matrix(y_true, y_pred)
    t_n, f_p, f_n, t_p = cm.ravel()

    return {
        'report': classification_report(y_true, y_pred, output_dict=True),
        'confusion_matrix': {
            't_n':f'{t_n}',
            'f_p':f'{f_p}',
            'f_n':f'{f_n}',
            't_p':f'{t_p}'
        }
    }

def load_data(path: str):
    '''
    Return data containing X_train, X_test, y_train, y_test
    '''
    with open(Path(path)/'data_bin.pkl', 'rb') as file:
        return pickle.load(file)

def pipeline_definition(features: Dict[str, List[str]], model_name:str, params: Dict[str, Any])-> Pipeline:
    return Pipeline([
            ('RareLabelEncoder', RareLabelEncoder(variables=features['CATEGORICAL'], ignore_format=True, tol=.05)),
            ('CountFrequencyEncoder', CountFrequencyEncoder(variables=features['CATEGORICAL'])),
            ('MathFeatures', MathFeatures(
                variables=features['NUMERICAL'],
                func=['mean'],
                drop_original=True,
                new_variables_names=['mean_inflation_gdp'])),
            (model_name, XGBClassifier(**params))
    ])

def mlflow_experiment(mlflow, hyper_params: Dict[str, Any], data, features: Dict[str, List[str]]):
    X_train, X_test, y_train, y_test = data

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)

    with mlflow.start_run():
        MODEL_NAME = 'XGBClassifier'

        mlflow.set_tag('model', MODEL_NAME)
        mlflow.set_tag('Undersampling', 'TomekLinks')
        mlflow.log_params(hyper_params)

        pipeline = pipeline_definition(features, MODEL_NAME, hyper_params)
        pipeline.fit(X_train, y_train)

        train_metrics = metrics(pipeline, X_train, y_train)
        test_metrics = metrics(pipeline, X_test, y_test)

        mlflow.log_dict({
            'columns': X_train.columns.tolist(),
            'data_types': X_train.dtypes.astype('str').to_dict()
        }, 'dataset_schema.json')

        train_accuracy, test_accuracy = train_metrics['report']['accuracy'], test_metrics['report']['accuracy']

        print(f'{test_accuracy=}')

        mlflow.log_metric('train_accuracy', train_accuracy)
        mlflow.log_metric('test_accuracy', test_accuracy)
        mlflow.log_dict(test_metrics, 'test_metrics.json')
        mlflow.sklearn.log_model(pipeline, artifact_path='model')

        with open('label_encoder.pkl', 'wb') as file:
            pickle.dump(label_encoder, file)

        # Log the serialized LabelEncoder file as an artifact in MLflow
        mlflow.log_artifact('label_encoder.pkl', artifact_path='encoders')

        return test_accuracy

params = get_params()