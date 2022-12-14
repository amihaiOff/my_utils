import json
import yaml


def save_json(data: dict, path: str, indent=4, ensure_ascii=False, **kwargs):
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, **kwargs)


def read_json(path: str, **kwargs):
    with open(path, 'r') as f:
        return json.load(f, **kwargs)


def read_yaml(path: str):
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def save_yaml(data: dict, path: str, **kwargs):
    with open(path, 'w') as f:
        yaml.dump(data, f, **kwargs)


def reindent_yaml(path: str):
    """
    sometimes yaml files are saved like json files and are not indented (one long line).
    This function reindents the yaml file.
    :param path:
    :return:
    """
    yaml_data = read_json(path)
    save_yaml(yaml_data, path)
