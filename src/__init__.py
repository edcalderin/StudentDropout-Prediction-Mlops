from pathlib import Path

import yaml
from yaml import SafeLoader


def get_params():
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, encoding='utf-8') as file:
        return yaml.load(file, Loader=SafeLoader)


params = get_params()
