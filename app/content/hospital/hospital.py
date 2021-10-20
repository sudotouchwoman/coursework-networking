'''
Business-process for hospital (yet in a single module)
'''
from app.database.query import SelectQuery
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-hospital-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=1)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info(msg=f'LOG STARTED: [{datetime.datetime.now(tz=None)}]')

DB_CONFIG_FILE = 'db-configs/db-hospital.json'

def load_db_config(path:str = DB_CONFIG_FILE) -> dict:
    from json import loads
    with open(path, 'r') as confile:
        settings = loads(confile.read())
    return settings

class HospitalController:
    def __init__(self, db_settings:dict) -> None:
        if db_settings is None: raise TypeError
        self.SETTINGS = db_settings

    def get_department_list(self) -> tuple:
        # candidate for caching
        log.debug(msg=f'Fetches department list')
        selected = SelectQuery(self.SETTINGS)\
            .execute_raw_query('SELECT department.department_name from department;')
        
        if selected is None:
            log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return (False,)
        
        selected = (row[0] for row in selected)
        log.debug(msg=f'Fetched department list')
        return (True, selected)

    def get_departments_report(self, department:str):
        # assume that department is already sanutized (used with html select tag)
        # repeated validation might be expensive to perform
        # utilization of cache may be a good idea

        log.debug(msg=f'Produces report for selected department {department}')

        selected = SelectQuery(self.SETTINGS)\
                .execute_raw_query(f'''
                SELECT department.department_head as 'Head', 
                SUM(chamber.totalspace) as 'Total space' 
                from department JOIN chamber ON chamber.department = id_department
                WHERE department.department_name like "{department}"
                GROUP BY id_department;
                            ''')

        if selected is None:
            log.error(msg=f'Failed to create report: is SQL server running? See db logs for more detailed info')
            return (False,)

        selected = selected[0]
        
        # I considered it to be a good idea to split one query with two joins into two sequential
        # such request would be performed faster
        # there are funny moves with fetched data as SelectQuery merely redirects pymysql results, which is formed by a list of tuples
        # in this particular case we would only return a single row thus I assign selected = selected[0]
        # to avoid messy double indices
        head_name = SelectQuery(self.SETTINGS)\
            .execute_raw_query(f'''
            SELECT doctor.first_name, second_name from doctor WHERE id_doctor = {selected[0]};
            '''
            )
        
        if head_name is None:
            log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with id = {selected[0]}')
            return (False,)

        selected = list(selected)
        selected[0] = ' '.join(head_name[0])
        selected = tuple(selected)
        log.debug(msg=f'Created report: {selected}')
        return (True, selected)

    def get_doctors(self):
        # also condidate for caching
        log.debug(msg=f'Fetches list of doctors')
        selected = SelectQuery(self.SETTINGS)\
            .execute_raw_query('SELECT doctor.second_name from doctor;')

        if selected is None:
            log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return (False,)

        selected = (row[0] for row in selected)
        log.debug(msg=f'Fetched list of doctors')
        return (True, selected)


    def get_assigned_to_doctor(self, doctor:str):

        log.debug(msg=f'Collects assignees for {doctor}')

        selected = SelectQuery(self.SETTINGS)\
            .execute_raw_query(
        f'''select
            patient.firstname,
            patient.secondname,
            patient.initial_diagnosis, 
            patient.outcome_diagnosis 
            from patient join doctor on attending_doctor = doctor.id_doctor 
            and doctor.second_name like '{doctor}';'''
                            )

        if selected is None:
            log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with creditentials {doctor}')
            return (False,)

        handle_null = lambda s: 'No information avaliable' if s == '' or s is None else s
        
        for i, row in enumerate(selected):
            row = list(row)
            row[1] = ' '.join(row[:2])
            row[2] = handle_null(row[2])
            row[3] = handle_null(row[3])
            row[0] = i + 1
            selected[i] = tuple(row)
        
        log.debug(msg=f'Successfully fetched report for given doctor')
        return (True, selected)



GLOBAL_HOSPITAL_CONTROLLER = HospitalController(load_db_config(DB_CONFIG_FILE))
