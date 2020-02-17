import yaml


def parse_config(filename: str) -> dict:
    """
    Parse YAML configuration.

    Parameters
    ----------
    filename: str
        Filename of the YAML configuration

    Returns
    -------
    dict
        Dictionary representation of contents in the YAML file

    """
    config = yaml.load(open(filename), Loader=yaml.FullLoader)
    return config
