from typing import List

import pandas as pd
from sqlalchemy import create_engine

POSTGRES_HOSTNAME = 'localhost'
POSTGRES_USER = 'user'
POSTGRES_PASSWORD = '123'
POSTGRES_DB = 'db_test'
POSTGRES_PORT = '5432'

psycopg_conn = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(psycopg_conn)

columns_dict = {
    'EVIDENTLY': [
        'drift_detected',
        'column_drift_metric',
        'number_of_drifted_columns',
        'current_share_of_missing_values',
        'reference_share_of_missing_values',
        'timezone',
    ],
    'HISTORICAL': [
        'GDP',
        'Inflation rate',
        'Tuition fees up to date',
        'Scholarship holder',
        'Curricular units 1st sem (approved)',
        'Curricular units 1st sem (enrolled)',
        'Curricular units 2nd sem (approved)',
        'prediction',
        'timezone',
    ],
}


def test_table(
    table_name: str, expected_columns: List[str], expected_row_numbers: int
) -> None:
    results = pd.read_sql_table(table_name, engine)

    print('Shape detected:', table_name, results.shape)

    assert (
        results.shape[0] == expected_row_numbers
    ), f'Number of rows in the table {table_name} does not match'
    assert results.shape[1] == len(
        expected_columns
    ), f'Number of columns in the table {table_name} does not match'
    assert (
        results.columns.to_list() == expected_columns
    ), f'Columns in the the table {table_name} do not match with the expected ones'


test_table('evidently_metrics', columns_dict['EVIDENTLY'], 1)

test_table('historical_data', columns_dict['HISTORICAL'], 1)
