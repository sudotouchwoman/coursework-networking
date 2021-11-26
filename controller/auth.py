import logging
from logging.handlers import TimedRotatingFileHandler
from os import getenv

from flask import current_app

from database.ORM import DataSource

DB_CONFIG = current_app.config['DB'].get('auth', None)
SQL_DIR = current_app.config.get('QUERIES', None)

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/auth.log')
log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

class PolicyController:
    def __init__(self, config: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if config is None or sql_dir is None:
            raise ValueError(f'Invalid args provided to {self.__class__.__name__}')
        self.SETTINGS = config
        self.SQL = sql_dir


    def map_credentials(self, login: str, password: str) -> str or None:

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('validate-user-credentials', login, password)
        try:
            selected = list(selected)
            selected = selected[0]
            return {
                'id': selected[0],
                'name': selected[1],
                'group': selected[2]
            }
        except (TypeError, IndexError):
            return
