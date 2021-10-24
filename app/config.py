import os
from abc import ABC
from . import load_json_config

class Config(ABC):
    HOST = os.getenv('HOST_NAME', '127.0.0.1')
    PORT = os.getenv('PORT', 5000)
    DEBUG = bool(os.getenv('DEBUG', "True") == "True")
    ENCODING = os.getenv('ENCODING', 'utf-8')
    SECRET_KEY = os.getenv('APP_SECRET_KEY', 'cringe')
    POLICIES = load_json_config('config/policies.json')
    DB = load_json_config('config/db.json')

class DevConfig(Config):

    HOST = os.getenv('DEV_HOST_NAME', '127.0.0.1')
    PORT = os.getenv('DEV_PORT', 5001)
    SECRET_KEY = 'dev'
    DEBUG = True
