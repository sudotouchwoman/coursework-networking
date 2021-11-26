import logging
from logging.handlers import TimedRotatingFileHandler
from os import getenv

from pymysql.err import ProgrammingError, OperationalError

from . import connect

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('DB_LOGFILE_NAME', 'logs/log-db-connection.log')
log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
# handler = logging.FileHandler(filename=f'{LOGFILE}', encoding='utf-8')
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

class Query():
    '''
    Base class for executing queries

    If a given query fails at some point, rule of thumb is to catch such error and return `None`

    Accepts settings from specified `connection_settings` dict
    '''
    DB_CONFIG = None

    def __init__(self, connection_settings:dict):
        self.DB_CONFIG = connection_settings
        return


    def execute_raw_query(self, raw:str):
        # execute "raw" query, i.e. without processing it
        # can be dangerous, but generally easier to use
        # must only be called for sanitized (preprocessed) inputs!
        log.debug(msg=f'Executes given raw query')
        if not isinstance(raw, str): raise TypeError
        
        log.debug(msg=f'Query is: {raw}')
        try:
            with connect.Connection(self.DB_CONFIG) as conn:
                if not conn.CONNECTED: return
                conn.CURSOR.execute(query=raw)
                fetched = [row for row in conn.CURSOR.fetchall()]
                log.debug(msg=f'Fetched {len(fetched)} rows')
                log.debug(msg=f'Fetched this: {fetched}')
                return fetched
        except (OperationalError, ProgrammingError):
            log.error(msg=f'Encountered error during execution')
            return


    def execute_with_args(self, query: str, *args) -> tuple or None:

        log.debug(msg=f'Executes query with params: {args}')
        log.debug(msg=f'Request is: {query}')

        try:
            with connect.Connection(self.DB_CONFIG) as conn:
                if not conn.CONNECTED: return
                conn.CURSOR.execute(query, args)
                fetched = ( row for row in conn.CURSOR.fetchall() )
                log.debug(msg=f'Affected {conn.CURSOR.rowcount} rows')
                log.debug(msg=f'Fetched this: {fetched}')
                return fetched
        except (OperationalError, ProgrammingError):
            log.error(msg=f'Encountered error during execution')
            return
            
        