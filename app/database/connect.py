from pymysql import connect
from pymysql.err import InterfaceError, OperationalError, Error
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('DB_LOGFILE_NAME', 'log-db-connection.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info(msg=f'LOG STARTED: [{datetime.datetime.now(tz=None)}]')

class Connection:
    '''
    Wrapper for `pymysql` cursor and connection to ease database routines

    Has `__enter__` and `__exit__` methods to be used with `with`
    '''
    CONNECTION = None
    CURSOR = None
    DB_CONFIG = None
    CONNECTED = False

    def __init__(self, config:dict) -> None:
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
            # return oerr
            # raise OperationalError('Connection aborted (Operational error)')
        except InterfaceError as ierr:
            log.error(msg=f'Uncatched exception occured: {ierr}')
            # return ierr
            # raise InterfaceError('Connection aborted (Interface error)')
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
            log.debug(msg=f'Exception info: {exc_type}::{exc_val}')
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

def test_connection(filename: str) -> bool:
    # simple test for connection
    # does not involve cursor execution
    # merely check SQL server avaliability
    log.info(msg='Test started')

    from json import loads
    try:
        with open(filename,'r') as confile:
            CONFIG = loads(confile.read())
        with Connection(config=CONFIG) as conn:
            log.info(msg='Connection established') if conn.CONNECTED else log.fatal(msg=f'Connection refused!')
    except FileNotFoundError as fe:
        log.error(msg=f'Failed to open config file: {fe}, stopping')
        return False
    log.info(msg='Test finished succesfully') if conn.CONNECTED else log.fatal(msg=f'Test failed!')
    return conn.CONNECTED

if __name__ == '__main__':
    test_connection('../../db-config.json')