'''
Business-process for hospital (yet in a single module)
'''
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import current_app

from app.database.ORM import DataSource

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-hospital-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

DB_CONFIG = current_app.config['DB'].get('hospital', None)
SQL_DIR = current_app.config.get('QUERIES', None)

class HospitalController:
    def __init__(self, db_settings: dict, sql_dir: str) -> None:
        if db_settings is None or sql_dir is None:
            log.fatal(msg=f'Recieved this: {db_settings} and {sql_dir}')
            log.fatal(msg=f'Failed to create Hospital controller! Is `hospital` in db config?')
            raise TypeError('Failed to create Hospital  controller')
        self.SETTINGS = db_settings
        self.SQL = sql_dir

    def get_department_list(self) -> tuple:
        # candidate for caching
        log.debug(msg=f'Fetches department list')
        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('department-list')

        if selected is None:
            log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return (False,)
        
        def process_rows():
            for row in selected:
                yield row[0]

        log.debug(msg=f'Fetched department list')
        return (True, process_rows())

    def get_departments_report(self, department:str):
        # assume that department is already sanutized (used with html select tag)
        # repeated validation might be expensive to perform
        # utilization of cache may be a good idea

        log.debug(msg=f'Produces report for selected department {department}')

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('department-report', department)

        if selected is None:
            log.error(msg=f'Failed to create report: is SQL server running? See db logs for more detailed info')
            return (False,)

        selected = list(selected)[0]
        
        # I considered it to be a good idea to split one query with two joins into two sequential
        # such request would be performed faster
        # there are funny moves with fetched data as SelectQuery merely redirects pymysql results, which is formed by a list of tuples
        # in this particular case we would only return a single row thus I assign selected = selected[0]
        # to avoid messy double indices
        head_name = DataSource(self.SETTINGS, self.SQL).fetch_results('select-doctor-initials', selected[0])

        if head_name is None:
            log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with id = {selected[0]}')
            return (False,)

        head_name = list(head_name)[0]

        def process_rows():
            yield ' '.join(head_name)
            yield selected[1]

        return (True, process_rows())

    def get_doctors(self):
        # also condidate for caching
        log.debug(msg=f'Fetches list of doctors')
        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('select-doctorlist')

        if selected is None:
            log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return (False,)

        def process_rows():
            for row in selected:
                yield row[0]

        log.debug(msg=f'Fetched list of doctors')
        return (True, process_rows())


    def get_assigned_to_doctor(self, doctor:str):

        log.debug(msg=f'Collects assignees for {doctor}')

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('hospital-assignment-list', doctor)

        if selected is None:
            log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with credentials {doctor}')
            return (False,)

        handle_null = lambda s: 'No information avaliable' if s == '' or s is None else s

        def process_rows():
            for i, row in enumerate(selected):
                new_row = (
                i + 1,
                ' '.join(row[:2]),
                handle_null(row[2]),
                handle_null(row[3]),
                )
                yield new_row
        
        log.debug(msg=f'Successfully fetched report for given doctor')
        return (True, process_rows())



GLOBAL_HOSPITAL_CONTROLLER = HospitalController(DB_CONFIG, SQL_DIR)
