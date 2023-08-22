from typing import Dict
from pathlib import Path

import yaml
from yaml.loader import SafeLoader


def get_params() -> Dict:
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, encoding='utf-8') as file:
        return yaml.load(file, Loader=SafeLoader)


params: Dict = get_params()
