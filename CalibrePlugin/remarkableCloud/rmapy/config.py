from pathlib import Path
from typing import Dict

from calibre.utils.config import JSONConfig

config = JSONConfig('plugins/remarkable_cloud')

def load() -> dict:
    return config


def dump(new_config: dict) -> None:
    global config
    config = new_config


