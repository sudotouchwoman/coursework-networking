import logging
from logging.handlers import TimedRotatingFileHandler
from os import getenv, walk
from os.path import isdir
from abc import ABC
from functools import lru_cache

from .query import Query

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('DB_LOGFILE_NAME', 'logs/db.log')

log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
# handler = logging.FileHandler(filename=f'{LOGFILE}', encoding='utf-8')
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

class ORM(ABC):
    @staticmethod
    @lru_cache(maxsize=1)
    def collect_queries(querydir: str) -> dict:
        log.info(msg=f'Collects queries from the provided path')
        if not isdir(querydir): raise NotADirectoryError
        queries = {
            file.replace('/','.').split('.')[-2] : open(f'{dir}/{file}', mode='r').read()
            for dir, _, files in walk(querydir) for file in files }
        log.info(msg=f'Queries collected and cached')
        return queries


class DataSource(ORM):
    def __init__(self, config: dict, sql_dir: str) -> None:
        if not isinstance(config, dict): raise ValueError(f'Config should be a dict instance, given {config}')

        try:
            queries = ORM.collect_queries(sql_dir)
        except NotADirectoryError:
            log.error(msg=f'Error occured while collecting queries')
            raise RuntimeError(f'Failed to collect cached queries from {sql_dir}')

        self.config = config
        self.queries = queries
        log.debug(msg=f'Created DataSource')


    def fetch_results(self, query: str, *args) -> tuple or None:
        if query not in self.queries:
            log.error(msg=f'Unknown query provided: {query}. Abort')
            return
        log.debug(msg=f'Query found, fetching results')

        fetched = Query(self.config)\
            .execute_with_args(self.queries[query], *args)
        return fetched


class DataModifier(DataSource):
    def update_table(self, query: str, *args) -> None:
        if query not in self.queries:
            log.error(msg=f'Unknown query provided: {query}. Abort')
            return
        log.debug(msg=f'Query to update found, performing')

        result_status = Query(self.config)\
            .execute_with_args(self.queries[query], *args)
        log.debug(msg=f'Query executed with status {result_status}')
