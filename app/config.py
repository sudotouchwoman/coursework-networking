from os import getenv
from abc import ABC

from . import load_json_config

class Config(ABC):
    HOST = getenv('HOST_NAME', '127.0.0.1')
    PORT = getenv('PORT', 5000)
    DEBUG = bool(getenv('DEBUG', "True") == "True")
    ENCODING = getenv('ENCODING', 'utf-8')
    SECRET_KEY = getenv('APP_SECRET_KEY', 'cringe')
    POLICIES = load_json_config('config/policies.json')
    DB = load_json_config('config/db.json')
    QUERIES  = getenv('SQL_QUERY_DIR', 'sql/')


class DevConfig(Config):

    HOST = getenv('DEV_HOST_NAME', '127.0.0.1')
    PORT = getenv('DEV_PORT', 5001)
    SECRET_KEY = 'dev'
    DEBUG = True
