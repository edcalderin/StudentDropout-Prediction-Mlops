# pylint: disable=import-error
import pickle
from typing import Any, Dict, Tuple
from pathlib import Path

import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from feature_engine.creation import MathFeatures
from feature_engine.encoding import RareLabelEncoder, CountFrequencyEncoder


def export_dataset(config: Dict, splited_data: Tuple) -> None:
    print('Creating pickle file...')
    pkl_name = Path(config['data']['preprocessed']) / 'data_bin.pkl'
    with open(pkl_name, 'wb') as file:
        pickle.dump(splited_data, file)


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


def load_data(path):
    '''
    Return data containing X_train, X_test, y_train, y_test
    '''
    with open(Path(path) / 'data_bin.pkl', 'rb') as file:
        return pickle.load(file)


def pipeline_definition(
    model, features: Dict, model_name: str, hyperparams: Dict[str, Any]
) -> Pipeline:
    return Pipeline(
        [
            (
                'RareLabelEncoder',
                RareLabelEncoder(
                    variables=features['categorical'], ignore_format=True, tol=0.05
                ),
            ),
            (
                'CountFrequencyEncoder',
                CountFrequencyEncoder(variables=features['categorical']),
            ),
            (
                'MathFeatures',
                MathFeatures(
                    variables=features['numerical'],
                    func=['mean'],
                    drop_original=True,
                    new_variables_names=['mean_inflation_gdp'],
                ),
            ),
            (model_name, model(**hyperparams)),
        ]
    )


def mlflow_experiment(mlflow, hyperparams, config: Dict, log_artifacts=False):
    # pylint: disable=too-many-locals

    X_train, X_test, y_train, y_test = load_data(config['data']['preprocessed'])

    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(y_train)
    y_test = label_encoder.transform(y_test)

    with mlflow.start_run():
        model = XGBClassifier
        model_name = type(model()).__name__

        mlflow.set_tag('model', model_name)
        mlflow.log_params(hyperparams)

        pipeline = pipeline_definition(
            model,
            config['features'],
            model_name,
            hyperparams,
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

        if log_artifacts:
            mlflow.sklearn.log_model(pipeline, artifact_path='model')

            # Log the serialized LabelEncoder file as an artifact in MLflow
            X_train['prediction'] = label_encoder.inverse_transform(
                pipeline.predict(X_train)
            )
            print('Logging training dataset and label encoder object')

            with open('artifacts.pkl', 'wb') as file:
                pickle.dump((label_encoder, X_train), file)

            mlflow.log_artifact('artifacts.pkl', artifact_path='artifacts')

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
