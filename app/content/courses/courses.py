'''
Business-process for courses (yet in a single module)
'''
import os
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import current_app

from app.database.ORM import DataModifier, DataSource

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
    'Japanese':'JP',
    'German' : 'German'
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


    def add_service(self, new_row: dict):
        log.debug(msg=f'Got request to edit table of services')
        
        with_tutor = lambda t: 1 if t == 'on' else 0
        lang_code = lambda l: COURSES_LANGUAGE_MAP_R.get(l, 'Any')
        
        row_sanitized = (
            lang_code(new_row.get('language')),
            new_row.get('title', 'Courses'),
            new_row.get('price', None),
            with_tutor(new_row.get('tutor', 0))
        )
        DataModifier(self.SETTINGS, self.SQL).update_table('insert-new-service', *row_sanitized)


    def remove_service(self, service_id: str):
        log.debug(msg=f'Got request to remove table item')
        if not service_id.isdigit():
            log.warning(msg=f'Wrong id encountered: {service_id}, abort')
            return
        DataModifier(self.SETTINGS, self.SQL).update_table('delete-service', service_id)


    def fetch_all_services(self) -> tuple:
        log.debug(msg=f'Got request to fetch all services')
        log.debug(msg=f'Performs query')

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('cart-fetch-services')
        log.debug(msg=f'Finished query')
        if selected is None: return (False,)

        has_tutor = lambda b: "With tutor" if (b > 0) else "Without tutor"
        pretty_print_price = lambda p: f'{int(p)}'

        def process_rows():
            for row in selected:
                yield {
                    'service_id': row[0],
                    'service_name': row[1],
                    'has_tutor': has_tutor(row[2]),
                    'lang': row[3],
                    'price': pretty_print_price(row[4])
                }

        log.debug(msg=f'Successfully collected from table, now returns results')
        return (True, process_rows())

    def find_service(self, service_id: str) -> tuple:
        log.debug(msg=f'Got request to lookup service')
        if not service_id.isdigit():
            log.warning(msg=f'Wrong id encountered: {service_id}, abort')
            return (False,)
        service_data = DataSource(self.SETTINGS, self.SQL).fetch_results('cart-find-service', service_id)
        if service_data is None: return (False,)

        has_tutor = lambda b: "With tutor" if (b > 0) else "Without tutor"
        pretty_print_price = lambda p: f'{int(p)}'
        service_data = list(service_data)[0]
        return (
            True,
            {
            'service_id': service_data[0],
            'service_name': service_data[1],
            'has_tutor': has_tutor(service_data[2]),
            'lang': service_data[3],
            'price': pretty_print_price(service_data[4])
            })

    
    def create_new_order(self, order_details: list, client: str) -> None:
        log.debug(msg=f'Got request to create new order!')
        if not isinstance(order_details, list):
            log.warning(msg=f'Order details are invalid, abort')
            return
        if len(order_details) == 0:
            log.warning(msg=f'The order details are empty, abort')
            return

        today = datetime.date.today().isoformat()
        total_price = sum([int(service['price']) for service in order_details])

        DataModifier(self.SETTINGS, self.SQL).update_table('create-order', client, today, total_price)
        log.debug(msg=f'Created new record in orders')


GLOBAL_COURSE_CONTROLLER = CourseController(DB_CONFIG, SQL_DIR)
