import os
import yaml


def read_yaml(path):
    with open(path) as f:
        yaml_content = os.path.expandvars(f.read())
        return yaml.load(yaml_content, Loader=yaml.FullLoader)


def read_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    return str()


def write_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)
    return True
