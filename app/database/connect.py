import pymysql
import logging
import datetime
import os

log = logging.getLogger(__name__)
DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
log.setLevel(getattr(logging, DEBUGLEVEL))
log.disabled = os.getenv('LOG_ON', "True") == "False"
handler = logging.FileHandler(filename=f'log-connection.log', encoding='utf-8')
formatter = logging.Formatter('[%(levelname)s]::[%(name)s]::%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info(msg=f'{__name__} LOG STARTED:\t[{datetime.datetime.now(tz=None)}]')

class Connection:
    CONNECTION = None
    DB_CONFIG = None

    def __init__(self, config:dict) -> None:
        self.DB_CONFIG = config
        log.debug(msg=f'{__name__} Initialized config with {config}')

    def __enter__(self):
        self.CONNECTION = pymysql.connect(
            host=self.DB_CONFIG['HOST'],
            port=self.DB_CONFIG['PORT'],
            user=self.DB_CONFIG['USER'],
            password=self.DB_CONFIG['PASSWORD'],
            database=self.DB_CONFIG['SCHEMA']
        )
        log.debug(msg=f'{__name__} Created connection')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.CONNECTION is None: return
        log.debug(msg=f'{__name__} Exception info: {exc_type}::{exc_val}::{exc_tb}')
        self.CONNECTION.close()

def test_connection() -> bool:
    log.info(msg='Test started')

    import json
    try:
        with open('db-config.json','r') as confile:
            CONFIG = json.loads(confile.read())
        with Connection(config=CONFIG) as conn:
            log.info(msg=f'Connection succeded')
            input('press any key to close connection:')
    except FileNotFoundError as fe:
        log.error(msg=f'Failed to open config file: {fe}, stopping')
        return False
    except Exception as e:
        log.error(msg=f'Encountered error: {e}, stopping')
        return False

    log.info(msg='Test finished')
    return True

if __name__ == '__main__':
    test_connection()