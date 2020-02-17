import yaml


def parse_config(file):
    config = yaml.load(open(file), Loader=yaml.FullLoader)
    return config
