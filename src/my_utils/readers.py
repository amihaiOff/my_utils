import json


def save_json(data, path, indent=4, ensure_ascii=False):
    with open(path, 'w') as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)
