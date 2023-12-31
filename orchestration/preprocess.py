# pylint: disable=import-error
import io
from typing import Dict, List, Tuple
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import requests
from prefect import flow, task
from imblearn.under_sampling import TomekLinks
from sklearn.model_selection import KFold

from config.params import params
from orchestration.common import export_dataset


@task(name='Read data')
def read_data(data_config: Dict) -> pd.DataFrame:
    print(f"Downloading data from {data_config['origin']}")
    response = requests.get(data_config['origin'], timeout=1)

    print(f"Extracting to {data_config['target_path']}")
    with ZipFile(io.BytesIO(response.content), 'r') as zip_file:
        zip_file.extractall(path=data_config['target_path'])

    df = pd.read_csv(
        Path(data_config['target_path']) / 'data.csv', sep=';', encoding='utf-8'
    )
    return df.query('Target!="Enrolled"').reset_index(drop=True)


@task(name='Resampling')
def resampling(df: pd.DataFrame, config: Dict) -> Tuple[pd.DataFrame, pd.Series]:
    features: List[str] = sum(config['features'].values(), [])

    X, y = df[features], df[config['target']]

    tomek_links = TomekLinks(n_jobs=-1)
    student_df_resampled = tomek_links.fit_resample(X, y)
    X = student_df_resampled[0]
    y = student_df_resampled[1]
    return X, y


@task(name='Split dataset')
def split_dataset(X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame | pd.Series]:
    '''
    Return X_train, X_test, y_train, y_test
    '''
    kfold = KFold(n_splits=10, shuffle=True, random_state=100)
    for train_idx, test_idx in kfold.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

    return X_train, X_test, y_train, y_test


@flow(name='Preprocess data', log_prints=True)
def preprocess():
    df = read_data(params['data']['raw'])

    preprocessed_path = Path(params['data']['preprocessed'])
    Path.mkdir(preprocessed_path, exist_ok=True)

    print('Resampling data...')
    X, y = resampling(df, params)

    print('Splitting data...')
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    export_dataset(params, (X_train, X_test, y_train, y_test))


if __name__ == '__main__':
    preprocess()
