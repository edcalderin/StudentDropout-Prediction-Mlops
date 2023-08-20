from typing import Dict

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)

from orchestration.common import load_data


class EvidentlyReport:
    def __init__(self, numerical_features, categorical_features) -> None:
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features

    def get_column_mapping(self):
        return ColumnMapping(
            target=None,
            prediction='prediction',
            numerical_features=self.numerical_features,
            categorical_features=self.categorical_features,
        )

    def get_metrics(self, current_data) -> Dict:
        print('Getting metrics...')
        train_data, *_ = load_data()

        report = Report(
            metrics=[
                ColumnDriftMetric(column_name='prediction'),
                DatasetDriftMetric(),
                DatasetMissingValuesMetric(),
            ]
        )

        report.run(
            reference_data=train_data,
            current_data=current_data,
            column_mapping=self.get_column_mapping(),
        )

        return report.as_dict()['metrics']
