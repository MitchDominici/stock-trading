import json
import os
from datetime import datetime

timestamp = datetime.now().strftime("%Y-%m-%d__%H_%M_%S")
script_dir = os.path.dirname(os.path.abspath(__file__))
relative_dir = '../..'
relative_path = os.path.join(script_dir, relative_dir)


def write_file(filename, data):
    full_file_path = os.path.join(relative_path, filename)
    with open(full_file_path, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_file(filename, data, include_timestamp=True):
    if include_timestamp:
        filename = filename.replace('.json', f'_{timestamp}.json')
    full_file_path = os.path.join(relative_path, filename)
    create_dir_if_not_exists(os.path.dirname(full_file_path))
    with open(full_file_path, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_array_to_file(filename, data):
    filename = filename.replace('.json', f'_{timestamp}.json')
    full_file_path = os.path.join(relative_path, filename)
    create_dir_if_not_exists(os.path.dirname(full_file_path))
    with open(full_file_path, 'w') as f:
        json.dump([stock[0] for stock in data], f)


def read_json_file(filename):
    full_file_path = os.path.join(relative_path, filename)
    try:
        with open(full_file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.decoder.JSONDecodeError:
        return None


def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
