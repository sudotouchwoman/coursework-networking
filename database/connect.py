import logging
from logging.handlers import TimedRotatingFileHandler
from os import getenv

from pymysql import connect
from pymysql.err import InterfaceError, OperationalError, Error

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('DB_LOGFILE_NAME', 'logs/db.log')

log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

class Connection:
    '''
    Wrapper for `pymysql` cursor and connection to ease database routines

    Has `__enter__` and `__exit__` methods to be used with `with`
    '''
    CONNECTION = None
    CURSOR = None
    DB_CONFIG = None
    CONNECTED = False

    def __init__(self, config: dict) -> None:
        self.DB_CONFIG = config
        log.debug(msg=f'Initialized config with {config}')

    def __enter__(self):
        try:
            self.CONNECTION = connect(
                host=self.DB_CONFIG['HOST'],
                port=self.DB_CONFIG['PORT'],
                user=self.DB_CONFIG['USER'],
                password=self.DB_CONFIG['PASSWORD'],
                database=self.DB_CONFIG['SCHEMA']
            )
            log.debug(msg=f'Created connection')
            self.CURSOR = self.CONNECTION.cursor()
            self.CONNECTED = True
            return self
        except OperationalError as oerr:
            parse_connection_exception(oerr)
        except InterfaceError as ierr:
            log.error(msg=f'Uncatched exception occured: {ierr}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.CONNECTED:
            self.CONNECTION.commit()
            self.CURSOR.close()
            self.CONNECTION.close()
            log.debug(msg=f'Connection closed successfully')
        else:
            log.debug(msg=f'Connection was not opened, nothing to close')
        if exc_val is not None:
            log.warning(msg=f'Exception info: {exc_type}::{exc_val}')
            parse_cursor_exception(exc_val)

def parse_connection_exception(err: Error):
    # add more useful analysis for errors raised during connection to log
    if err.args[0] == 1049: log.error(msg=f'Invalid DB name')
    if err.args[0] == 1045: log.error(msg=f'Invalid creditentials: {err.args[1]}')
    if err.args[0] == 2003: log.error(msg=f'Host refused to connect: {err.args[1]}')

def parse_cursor_exception(err: Error):
    # add more useful analysis for errors raised during cursor execution to log
    if err.args[0] == 1146: log.error(msg=f'Invalid table name: {err.args[1]}')
    if err.args[0] == 1054: log.error(msg=f'Invalid column name: {err.args[1]}')
    if err.args[0] == 1064: log.error(msg=f'Invalid SQL syntax: {err.args[1]}')
