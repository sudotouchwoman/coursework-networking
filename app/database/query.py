import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pymysql.err import ProgrammingError, OperationalError

from . import connect

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('DB_LOGFILE_NAME', 'logs/log-db-connection.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
# handler = logging.FileHandler(filename=f'{LOGFILE}', encoding='utf-8')
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=1)
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
        return None

    def execute_query(self):
        raise NotImplementedError

    def execute_raw_query(self, raw:str):
        # execute "raw" query, i.e. without processing it
        # can be dangerous, but generally easier to use
        # must only be called for sanitized (preprocessed) inputs!
        log.debug(msg=f'Executes given raw query')
        if not isinstance(raw, str): raise TypeError
        
        log.debug(msg=f'Query is: {raw}')
        try:
            with connect.Connection(self.DB_CONFIG) as conn:
                if not conn.CONNECTED: return None
                conn.CURSOR.execute(query=raw)
                fetched = [row for row in conn.CURSOR.fetchall()]
                log.debug(msg=f'Fetched {len(fetched)} rows')
                log.debug(msg=f'Fetched this: {fetched}')
                return fetched
        except (OperationalError, ProgrammingError):
            log.error(msg=f'Encountered error during execution')
            return None
    
class SelectQuery(Query):
    def execute_query(self, rows:list, table:str, limit:str = None):
        '''
        Execute `SELECT` query for the given `table`. Selects `rows` with optional `limit`
        '''
        log.debug(msg=f'Executes query')
        SQL_QUERY = f'SELECT {", ".join(rows)} FROM {table}'
        if isinstance(limit, str) or isinstance(limit, int) and int(limit) > 0: SQL_QUERY += f' LIMIT {limit}'
        
        log.debug(msg=f'Query is: {SQL_QUERY}')
        try:
            with connect.Connection(self.DB_CONFIG) as conn:
                if not conn.CONNECTED: return None
                conn.CURSOR.execute(query=SQL_QUERY)
                fetched = [row for row in conn.CURSOR.fetchall()]
                log.debug(msg=f'Fetched {len(fetched)} rows')
                log.debug(msg=f'Fetched this: {fetched}')
                return fetched
        except (OperationalError, ProgrammingError):
            log.error(msg=f'Encountered error during execution')
            return None
