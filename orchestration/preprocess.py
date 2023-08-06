# pylint: disable=import-error
import io
import pickle
from typing import Dict, List, Tuple
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import requests
from common import params
from prefect import flow, task
from imblearn.under_sampling import TomekLinks
from sklearn.model_selection import KFold


@task(name='Read data')
def read_data(data_config: Dict) -> pd.DataFrame:
    print(f"Downloading data from {data_config['ORIGIN']}")
    response = requests.get(data_config['ORIGIN'], timeout=1)

    print(f"Extracting to {data_config['TARGET_PATH']}")
    with ZipFile(io.BytesIO(response.content), 'r') as zip_file:
        zip_file.extractall(path=data_config['TARGET_PATH'])

    df = pd.read_csv(
        Path(data_config['TARGET_PATH']) / 'data.csv', sep=';', encoding='utf-8'
    )
    return df.query('Target!="Enrolled"').reset_index(drop=True)


@task(name='Resampling')
def resampling(
    df: pd.DataFrame, dict_features: Dict[str, List[str]], target: str
) -> Tuple[pd.DataFrame, pd.Series]:
    features: List[str] = sum(dict_features.values(), [])

    X, y = df[features], df[target]

    tomek_links = TomekLinks(n_jobs=-1)
    student_df_resampled = tomek_links.fit_resample(X, y)
    X = student_df_resampled[0]
    y = student_df_resampled[1]
    return X, y


@task(name='Split dataset')
def split_dataset(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame | pd.Series]:
    kfold = KFold(n_splits=10, shuffle=True, random_state=100)
    for train_idx, test_idx in kfold.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

    return X_train, X_test, y_train, y_test


@flow(log_prints=True)
def preprocess():
    df = read_data(params['DATA']['RAW'])

    preprocessed_path = Path(params['DATA']['PREPROCESSED'])
    Path.mkdir(preprocessed_path, exist_ok=True)

    print('Resampling data...')
    X, y = resampling(df, params['FEATURES'], params['TARGET'])

    print('Splitting data...')
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    print('Creating pickle file...')
    NAME = preprocessed_path / 'data_bin.pkl'
    with open(NAME, 'wb') as file:
        pickle.dump((X_train, X_test, y_train, y_test), file)


if __name__ == '__main__':
    preprocess()
