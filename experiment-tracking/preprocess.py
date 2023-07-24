import pandas as pd
from zipfile import ZipFile
from pathlib import Path
import io
import requests
from common import params
from imblearn.under_sampling import TomekLinks
from typing import List, Dict, Tuple
from sklearn.model_selection import KFold
import pickle

def read_data(data_config: Dict)->pd.DataFrame:
    response = requests.get(data_config['ORIGIN'])

    with ZipFile(io.BytesIO(response.content), 'r') as zip_file:
        zip_file.extractall(path=data_config['TARGET_PATH'])

    return pd.read_csv(Path(data_config['TARGET_PATH'])/'data.csv', sep=';', encoding='utf-8')

def resampling(X: pd.DataFrame, y:pd.Series)->Tuple[pd.DataFrame, pd.Series]:
    tomek_links = TomekLinks(n_jobs=-1)
    student_df_resampled = tomek_links.fit_resample(X, y)
    X = student_df_resampled[0]
    y = student_df_resampled[1]
    return X, y

def split_dataset(df: pd.DataFrame, dict_features: Dict[str, List[str]], target:str)-> Tuple[pd.DataFrame | pd.Series]:
    features: List[str] = sum(dict_features.values(), [])

    X = df[features]
    y = df[target]

    X, y = resampling(X, y)

    kfold = KFold(n_splits = 10, shuffle = True, random_state = 100)
    for train_idx, test_idx in kfold.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

    return X_train, X_test, y_train, y_test

def preprocess()->pd.DataFrame:
    df = read_data(params['DATA']['RAW'])
    df = df.query('Target!="Enrolled"').reset_index(drop=True)

    preprocessed_path = Path(params['DATA']['PREPROCESSED'])
    Path.mkdir(preprocessed_path, exist_ok=True)

    X_train, X_test, y_train, y_test = split_dataset(df, params['FEATURES'], params['TARGET'])

    NAME = preprocessed_path/'data_bin.pkl'
    with open(NAME, 'wb') as file:
        pickle.dump((X_train, X_test, y_train, y_test), file)

preprocess()