
from calibre.utils.config import JSONConfig

config = JSONConfig('plugins/remarkable_ssh_driver')
# cache used to match books between remarkable and calibre libraries.
# key = remarkable id, value = [calibre id, [authors]] (tuple was converted to list with JsonConfig)
config.defaults['match_cache'] = None


def load() -> dict:
    global config
    return config


def dump() -> None:
    global config
    config.commit()