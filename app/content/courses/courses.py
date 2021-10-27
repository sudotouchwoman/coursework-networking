'''
Business-process for courses (yet in a single module)
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
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-courses-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

DB_CONFIG = current_app.config['DB'].get('courses', None)
SQL_DIR = current_app.config.get('QUERIES', None)

COURSES_LANGUAGE_MAP_R = {
    'All languages' : '%',
    'English' : 'EN',
    'French' : 'FR',
    'Japanese':'JP'
}

class CourseController:
    def __init__(self, db_settings: dict, sql_dir: str) -> None:
        if db_settings is None or sql_dir is None:
            log.fatal(msg=f'Recieved this: {db_settings} and {sql_dir}')
            log.fatal(msg=f'Failed to create courses controller! Is `courses` in db config?')
            raise TypeError('Failed to create courses controller')
        self.SETTINGS = db_settings
        self.SQL = sql_dir

    def get_services_for_language(self, language:str) -> tuple:
        log.debug(msg=f'Gets services for {language} language')
        if language not in COURSES_LANGUAGE_MAP_R: return (False,)
        log.debug(msg=f'{language} was found in the map')
        language = COURSES_LANGUAGE_MAP_R[language]
        
        log.debug(msg=f'Performs query')
        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('select-services-by-lang', language)

        log.debug(msg=f'Finished query')
        if selected is None: return (False,)
        
        has_tutor = lambda b: "With tutor" if (b > 0) else "Without tutor"
        pretty_print_price = lambda p: f'{int(p)}'

        def process_rows():
            for row in selected:
                yield (
                    row[0],
                    row[1],
                    has_tutor(row[2]),
                    row[3],
                    pretty_print_price(row[4])
                )
        
        log.debug(msg=f'Successfully collected from table, now returns results')
        return (True, process_rows())

    def get_orders_for_threshold(self, threshold:str) -> tuple:
        log.debug(msg=f'Gets orders with thresh of {threshold}')

        if not threshold.isdigit():
            log.error(msg=f'Provided value is not a valid digit, abort')
            return (False,)

        log.debug(msg=f'Performs query')
        filtered = DataSource(self.SETTINGS, self.SQL).fetch_results('select-orders-by-thresh', threshold)
        log.debug(msg=f'Finished query')
        
        log.debug(msg=f'Collected this: {filtered}')
        if filtered is None: return (False,)
        
        pretty_print_price = lambda p: f'{int(p)}'

        def process_rows():
            for row in filtered:
                new_row = list(row)
                new_row[3] = pretty_print_price(new_row[3])
                yield new_row
        
        log.debug(msg=f'Successfully collected from table, now returns results')
        return (True, process_rows())

GLOBAL_COURSE_CONTROLLER = CourseController(DB_CONFIG, SQL_DIR)
