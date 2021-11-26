'''
Business-process for hospital (yet in a single module)
'''
from os import getenv, name
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import current_app

from database.ORM import DataSource, DataModifier

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/hospital.log')
log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

DB_CONFIG = current_app.config['DB'].get('hospital')
SQL_DIR = current_app.config.get('QUERIES')

class HospitalController:
    def __init__(self, db_settings: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if db_settings is None or sql_dir is None:
            log.fatal(msg=f'Recieved this: {db_settings} and {sql_dir}')
            log.fatal(msg=f'Failed to create Hospital controller! Is `hospital` in db config?')
            raise TypeError('Failed to create Hospital  controller')
        self.SETTINGS = db_settings
        self.SQL = sql_dir


    def get_department_list(self) -> None or tuple:
        # candidate for caching
        log.debug(msg=f'Fetches department list')
        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('department-list')

        if selected is None:
            log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return

        def process_rows():
            for row in selected:
                yield row[0]

        log.debug(msg=f'Fetched department list')
        return process_rows()


    def get_departments_report(self, department: str) -> None or tuple:
        # assume that department is already sanitized (used with html select tag)
        # repeated validation might be expensive to perform
        # utilization of cache may be a good idea

        log.debug(msg=f'Produces report for selected department {department}')

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('department-report', department)

        if selected is None:
            log.error(msg=f'Failed to create report: is SQL server running? See db logs for more detailed info')
            return

        selected = list(selected)[0]
        
        # I considered it to be a good idea to split one query with two joins into two sequential
        # such request would be performed faster
        # there are funny moves with fetched data as SelectQuery merely redirects pymysql results, 
        # which is formed by a list of tuples
        # in this particular case we would only return a single row thus I assign selected = selected[0]
        # to avoid messy double indices
        head_name = DataSource(self.SETTINGS, self.SQL).fetch_results('select-doctor-initials', selected[0])

        if head_name is None:
            log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with id = {selected[0]}')
            return

        head_name = list(head_name)[0]

        def process_rows():
            yield ' '.join(head_name)
            yield selected[1]

        return process_rows()


    def get_doctors(self) -> None or tuple:
        # also condidate for caching
        log.debug(msg=f'Fetches list of doctors')
        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('select-doctorlist')

        if selected is None:
            log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return

        def process_rows():
            for row in selected:
                yield {
                    'id': row[0],
                    'name': ' '.join(row[1:])
                    }

        log.debug(msg=f'Fetched list of doctors')
        return process_rows()


    def get_assigned_to_doctor(self, doctor) -> None or tuple:

        log.debug(msg=f'Collects assignees for {doctor}')

        selected = DataSource(self.SETTINGS, self.SQL).fetch_results('fetch-patients-filterby-doctor', doctor)

        if selected is None:
            log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with credentials {doctor}')
            return

        handle_null = lambda s: 'N/A' if s is None or not s else s

        def process_rows():
            for i, row in enumerate(selected):
                yield (
                i + 1,
                ' '.join(row[:2]),
                handle_null(row[2]),
                handle_null(row[3]),
                )
        
        log.debug(msg=f'Successfully fetched report for given doctor')
        return process_rows()


    def get_doctor_name(self, id_doctor) -> str or None:
        name = DataSource(self.SETTINGS, self.SQL).fetch_results('select-doctor-initials', id_doctor)
        if name is None: return
        return ' '.join(name[0])

    def check_chambers_capacity(self) -> int or None:
        log.debug(msg=f'Checks capacity of chambers')

        chamber_data = DataSource(self.SETTINGS, self.SQL).fetch_results('check-chambers')
        try:
            chamber_data = list(chamber_data)[0]
        except IndexError:
            log.error(msg=f'Chambers must be full')
            return
        except TypeError:
            log.error(msg=f'Error occured during db connection')
            return

        log.debug(msg=f'Chamber {chamber_data[0]} is the biggest chamber with free space')
        return chamber_data[0]

    
    def filter_appointments(self, by: str, value: str) -> None or tuple:
        options = {
            'doctor': 'fetch-appointments-filterby-doctor',
            'patient': 'fetch-appointments-filterby-patient',
            'status': 'fetch-appointments-filterby-status'
        }

        if by not in options.keys():
            log.error(msg=f'Invalid filter: {by}')
            return

        filtered = DataSource(self.SETTINGS, self.SQL)\
            .fetch_results(options[by], value)

        if filtered is None:
            log.warning(msg=f'Failed to fetch appointments satisfying {by}={value}')
            return

        handle_null = lambda s: 'N/A' if s is None or not s else s
        def handle_status_code(s: int) -> str:
            if s == 0: return 'Pending request'
            if s == 1: return 'Accepted'
            if s == 2: return 'Rejected'
            if s == 3: return 'Done'
            return 'Unknown status'


        def process_rows():
            for i, row in enumerate(filtered):
                try:
                    initials = DataSource(self.SETTINGS, self.SQL)\
                        .fetch_results('fetch-patient-initials', row[2])
                    initials = list(initials)[0]
                    yield {
                        'num': i,
                        'id': row[0],
                        'asignee': row[1],
                        'patient_id': row[2],
                        'patient': ' '.join(initials[5:7]),
                        'about': handle_null(row[4]),
                        'scheduled': handle_null(row[3]),
                        'status': handle_status_code(row[5]),
                        'status_code': row[5]
                    }
                except (TypeError, IndexError):
                    log.warning(msg=f'Exception occured while processing row: {row}')
                    yield {
                        'num': i,
                        'id': row[0],
                        'asignee': row[1],
                        'patient_id': row[2],
                        'patient': 'N/A',
                        'about': handle_null(row[4]),
                        'scheduled': handle_null(row[3]),
                        'status': handle_status_code(row[5]),
                        'status_code': row[5]
                    }


        log.debug(msg=f'Successfully fetched appointments')
        return process_rows()


    def update_appointment(self, action: str, appointment_id) -> None:
        options = {
            'complete': 3,
            'accept': 1,
            'reject': 2
            }

        if action not in options.keys():
            log.error(msg=f'Invalid action: {action}')
            return

        DataModifier(self.SETTINGS, self.SQL)\
            .update_table('update-appointment', options[action], appointment_id)
        

