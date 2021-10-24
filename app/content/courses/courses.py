'''
Business-process for courses (yet in a single module)
'''

import os
import logging
from logging.handlers import TimedRotatingFileHandler
from flask import current_app

from app.database.query import SelectQuery

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-courses-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=1)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

DB_CONFIG = current_app.config['DB'].get('courses', None)

COURSES_LANGUAGE_MAP_R = {
    'All languages' : '%',
    'English' : 'EN',
    'French' : 'FR',
    'Japanese':'JP'
}

class CourseController:
    def __init__(self, db_settings:dict) -> None:
        if db_settings is None:
            log.fatal(msg=f'Failed to create courses controller! Is `courses` in db config?')
            raise TypeError('Failed to create courses controller')
        self.SETTINGS = db_settings

    def get_services_for_language(self, language:str) -> tuple:
        log.debug(msg=f'Gets services for {language} language')
        if language not in COURSES_LANGUAGE_MAP_R: return (False,)
        log.debug(msg=f'{language} was found in the map')
        
        log.debug(msg=f'Performs query')
        selected = SelectQuery(self.SETTINGS)\
            .execute_raw_query(f'SELECT * FROM services WHERE language LIKE "{COURSES_LANGUAGE_MAP_R[language]}"')

        log.debug(msg=f'Finished query')
        log.debug(msg=f'Collected this: {selected}')
        if selected is None: return (False,)
        
        has_tutor = lambda b: "With tutor" if (b > 0) else "Without tutor"
        pretty_print_price = lambda p: f'{int(p)}'

        for i, row in enumerate(selected):
            # log.debug(msg=f'Row: {row}')
            selected[i] = list(selected[i])
            selected[i][2] = has_tutor(row[2])
            selected[i][4] = pretty_print_price(row[4])
        
        log.debug(msg=f'Successfully collected from table, now returns results')
        return (True, selected)

    def get_orders_for_threshold(self, threshold:str) -> tuple:
        log.debug(msg=f'Gets orders with thresh of {threshold}')

        if not threshold.isdigit():
            log.error(msg=f'Provided value is not a valid digit, abort')
            return (False,)

        def get_threshed_orders():
            return SelectQuery(self.SETTINGS)\
                .execute_raw_query(f'SELECT * FROM orders WHERE total_price > {threshold} ORDER BY total_price DESC')
        
        log.debug(msg=f'Performs query')
        filtered = get_threshed_orders()
        log.debug(msg=f'Finished query')
        
        log.debug(msg=f'Collected this: {filtered}')
        if filtered is None: return (False,)
        
        pretty_print_price = lambda p: f'{int(p)}'
        for i, row in enumerate(filtered):
            filtered[i] = list(filtered[i])
            filtered[i][3] = pretty_print_price(filtered[i][3])
        
        log.debug(msg=f'Successfully collected from table, now returns results')
        return (True, filtered)

GLOBAL_COURSE_CONTROLLER = CourseController(DB_CONFIG)
