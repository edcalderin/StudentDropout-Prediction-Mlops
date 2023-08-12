from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    ClassificationClassBalance,
    DatasetMissingValuesMetric,
    ClassificationConfusionMatrix,
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

    def create_report(self, file_name: str):
        report = Report(
            metrics=[
                ColumnDriftMetric(column_name='prediction'),
                DatasetDriftMetric(),
                DatasetMissingValuesMetric(),
                ClassificationClassBalance(),
                ClassificationConfusionMatrix(),
            ]
        )

        print('Analyzing report...')
        report.run(
            reference_data=self.train_data,
            current_data=self.test_data,
            column_mapping=self.get_column_mapping(),
        )

        print('Generating html report...')
        report.save_html(file_name)
