from typing import Dict

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)


class EvidentlyReport:
    # pylint: disable=too-many-arguments
    def __init__(
        self, train_data, test_data, numerical_features, categorical_features, target: str
    ) -> None:
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.train_data = train_data
        self.test_data = test_data
        self.target = target

    def get_column_mapping(self):
        return ColumnMapping(
            target=self.target,
            prediction='prediction',
            numerical_features=self.numerical_features,
            categorical_features=self.categorical_features,
        )

    def get_metrics(self) -> Dict:
        print('Getting metrics...')

        report = Report(
            metrics=[
                ColumnDriftMetric(column_name='prediction'),
                DatasetDriftMetric(),
                DatasetMissingValuesMetric(),
            ]
        )

        report.run(
            reference_data=self.train_data,
            current_data=self.test_data,
            column_mapping=self.get_column_mapping(),
        )

        return report.as_dict()['metrics']
