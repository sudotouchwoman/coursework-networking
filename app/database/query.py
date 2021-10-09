import logging
import os
import datetime
from pymysql.err import ProgrammingError, OperationalError

# have to import nearby module in such way as 
# somehow while importing from blueprints package it needs 
# first option, however at launch as __main__ 
# it breaks with `attempted relative import with no known parent package`
# well... there ARE parent packages as well as current directoty package
# python is weird, will resolve this conflict later maybe
try:
    # import after being imported as a module
    from . import connect
except ImportError:
    # import when being launched itself (i.e. for testing)
    import connect

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('DB_LOGFILE_NAME', 'log-db-connection.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = logging.FileHandler(filename=f'{LOGFILE}', encoding='utf-8')
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info(msg=f'LOG STARTED: [{datetime.datetime.now(tz=None)}]')

def load_db_config(path_to_config:str) -> dict:
    '''
    Load setting for db routines from `json` file at specified location `path_to_config`
    '''
    from json import loads
    with open(path_to_config) as confile:
        return loads(confile.read())

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
        if isinstance(limit, int) or int(limit) > 0: SQL_QUERY += f' LIMIT {limit}'
        
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

if __name__ == '__main__':
    # perform simple test for connecting to database and querying
    # test correct query and one containing errors
    # one problem bothering me is config source, should better use .py config instead of .json  one
    # everything seems to work fine
    
    log.info(msg=f'Testing query performance')

    query = SelectQuery(load_db_config(path_to_config='../../db-config.json'))          # load config from relative location ans pass to query
    rows = query.execute_query(['id_doctor', 'first_name', 'second_name'], 'doctor')    # success
    rows = query.execute_query(['id_patient', 'firstname', 'secondname'], 'patient')    # success
    rows = query.execute_query([], 'patient')   # fails and returns None

    log.info(msg=f'Test on query finished')
