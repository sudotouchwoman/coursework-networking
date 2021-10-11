import os

class Config:
    HOST = os.getenv('HOST_NAME', '127.0.0.1')
    PORT = os.getenv('PORT', 5000)
    DEBUG = bool(os.getenv('DEBUG', "True") == "True")
    ENCODING = os.getenv('ENCODING', 'utf-8')
    BASEDIR = os.getcwd()

class DevConfig(Config):

    HOST = os.getenv('DEV_HOST_NAME', '127.0.0.1')
    PORT = os.getenv('DEV_PORT', 5001)
    DEBUG = True
