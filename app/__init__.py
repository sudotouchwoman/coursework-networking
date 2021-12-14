import logging
from logging.handlers import TimedRotatingFileHandler
from os import getenv

def run_app():
    from view import create_app
    from . import config

    settings = config.DevConfig
    app = create_app(settings=settings)

    app.run(
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG)


def load_json_config(path: str) -> dict:
    from json import load
    with open(path, 'r') as confile:
        settings = load(confile)
    return settings

def make_logger(
    name: str,
    logfile: str) -> logging.Logger:

    log = logging.getLogger(name)

    if not log.hasHandlers(): 
        DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
        log.disabled = getenv('LOG_ON', "True") == "False"

        log.setLevel(getattr(logging, DEBUGLEVEL))

        formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
        handler = TimedRotatingFileHandler(filename=f'{logfile}', encoding='utf-8', when='h', interval=5, backupCount=0)
        handler.setFormatter(formatter)
        log.addHandler(handler)

    return log