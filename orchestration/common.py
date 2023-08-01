import pickle
from typing import Any, Dict, List
from pathlib import Path

import yaml
import pandas as pd
from xgboost import XGBClassifier
from yaml.loader import SafeLoader
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from feature_engine.creation import MathFeatures
from feature_engine.encoding import RareLabelEncoder, CountFrequencyEncoder

from orchestration.args_mlflow_experiment import ArgsMLFlowExperiment


def get_params():
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, encoding='utf-8') as file:
        return yaml.load(file, Loader=SafeLoader)


def metrics(model: Pipeline, X: pd.DataFrame, y_true: pd.Series) -> Dict[str, Any]:
    y_pred = model.predict(X)
    cm = confusion_matrix(y_true, y_pred)
    t_n, f_p, f_n, t_p = cm.ravel()

    return {
        'report': classification_report(y_true, y_pred, output_dict=True),
        'confusion_matrix': {
            't_n': f'{t_n}',
            'f_p': f'{f_p}',
            'f_n': f'{f_n}',
            't_p': f'{t_p}',
        },
    }


def load_data(path: str):
    '''
    Return data containing X_train, X_test, y_train, y_test
    '''
    with open(Path(path) / 'data_bin.pkl', 'rb') as file:
        return pickle.load(file)


def pipeline_definition(
    model, features: Dict[str, List[str]], model_name: str, hyperparams: Dict[str, Any]
) -> Pipeline:
    return Pipeline(
        [
            (
                'RareLabelEncoder',
                RareLabelEncoder(
                    variables=features['CATEGORICAL'], ignore_format=True, tol=0.05
                ),
            ),
            (
                'CountFrequencyEncoder',
                CountFrequencyEncoder(variables=features['CATEGORICAL']),
            ),
            (
                'MathFeatures',
                MathFeatures(
                    variables=features['NUMERICAL'],
                    func=['mean'],
                    drop_original=True,
                    new_variables_names=['mean_inflation_gdp'],
                ),
            ),
            (model_name, model(**hyperparams)),
        ]
    )


def mlflow_experiment(args_mlflow_experiment: ArgsMLFlowExperiment):
    X_train, X_test, y_train, y_test = load_data(args_mlflow_experiment.data_path)

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)

    mlflow = args_mlflow_experiment.mlflow
    with mlflow.start_run():
        model = XGBClassifier
        model_name = type(model()).__name__

        mlflow.set_tag('model', model_name)
        mlflow.log_params(args_mlflow_experiment.hyperparams)

        pipeline = pipeline_definition(
            model,
            args_mlflow_experiment.features,
            model_name,
            args_mlflow_experiment.hyperparams,
        )
        pipeline.fit(X_train, y_train)

        train_metrics = metrics(pipeline, X_train, y_train)
        test_metrics = metrics(pipeline, X_test, y_test)

        mlflow.log_dict(
            {
                'columns': X_train.columns.tolist(),
                'data_types': X_train.dtypes.astype('str').to_dict(),
            },
            'dataset_schema.json',
        )

        train_accuracy, test_accuracy = (
            train_metrics['report']['accuracy'],
            test_metrics['report']['accuracy'],
        )

        print(f'{test_accuracy = }')

        mlflow.log_metric('train_accuracy', train_accuracy)
        mlflow.log_metric('test_accuracy', test_accuracy)
        mlflow.log_dict(test_metrics, 'test_metrics.json')

        if args_mlflow_experiment.log_artifacts:
            mlflow.sklearn.log_model(pipeline, artifact_path='model')

            with open('label_encoder.pkl', 'wb') as file:
                pickle.dump(label_encoder, file)

            # Log the serialized LabelEncoder file as an artifact in MLflow
            mlflow.log_artifact('label_encoder.pkl', artifact_path='encoders')

        return test_accuracy


def parse_param(value: str):
    if value == 'True':
        return True
    if value == 'False':
        return False
    if value == 'None':
        return None

    try:
        try:
            return int(value)
        except ValueError:
            return float(value)
    except ValueError:
        return value


params = get_params()
