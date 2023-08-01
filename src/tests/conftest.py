import pytest


@pytest.fixture()
def feature_fixture():
    return {
        'GDP': 1.74,
        'Inflation rate': 1.4,
        'Tuition fees up to date': 1,
        'Scholarship holder': 0,
        'Curricular units 1st sem (approved)': 5,
        'Curricular units 1st sem (enrolled)': 6,
        'Curricular units 2nd sem (approved)': 5,
    }
