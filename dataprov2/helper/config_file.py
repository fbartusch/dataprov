import configparser
import os

from mkdir_p import mkdir_p


def create(path: str, config: configparser.ConfigParser) -> None:
    base_dir = os.path.dirname(path)
    # Create base directory if needed
    mkdir_p(base_dir)
    with open(path, "w") as configfile:
        config.write(configfile)
