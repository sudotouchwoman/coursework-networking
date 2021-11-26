'''
Business-process related to patients: add new patient, assign to doctor etc
'''
from os import getenv
import logging
from logging.handlers import TimedRotatingFileHandler

import datetime
from flask import current_app
from schema import *

from database.ORM import DataSource, DataModifier
from . import Validator

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/patients.log')
log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

DB_CONFIG = current_app.config['DB'].get('hospital')
SQL_DIR = current_app.config.get('QUERIES')

class PatientController:
    def __init__(self, db_settings: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if db_settings is None or sql_dir is None:
            log.fatal(msg=f'Recieved this: {db_settings} and {sql_dir}')
            log.fatal(msg=f'Failed to create Hospital controller! Is `hospital` in db config?')
            raise TypeError('Failed to create Hospital  controller')
        self.SETTINGS = db_settings
        self.SQL = sql_dir


    def create_patient_record(self, patient_data: dict) -> None:
        if patient_data is None:
            log.error(f'Patient creation aborted, the data is missing')
            return

        if not Validator.validate_patient_data(patient_data): 
            log.error(msg=f'Validation failed')
            return

        DataModifier(self.SETTINGS, self.SQL).update_table('update-chamber', patient_data['chamber'])

        patient_data = (
            patient_data['passport'], datetime.date.today().isoformat(),
            patient_data['date_birth'], patient_data['first_name'],
            patient_data['second_name'], patient_data['city'],
            patient_data['attending_doctor'], patient_data['chamber']
        )

        DataModifier(self.SETTINGS, self.SQL).update_table('create-patient-record', *patient_data)

    
    def fetch_all_patients(self) -> None or tuple:
        log.debug(msg=f'Fetches patient list')

        patients = DataSource(self.SETTINGS, self.SQL).fetch_results('fetch-patients')

        if patients is None:
            log.warning(msg=f'Failed to fetch patients. Is SQL Server running?')
            return

        handle_null = lambda s: 'N/A' if s is None or not s else s
        discharged = lambda s: s is None
        outcome_diag = lambda s: 'Unspecified' if s is None else s

        def process_rows():
            for i, row in enumerate(patients, start=1):
                try:
                    doctor_name = DataSource(self.SETTINGS, self.SQL)\
                        .fetch_results('select-doctor-initials', row[10])
                    doctor_name = list(doctor_name)[0]

                    yield {
                        'id': row[0],
                        'num': i,
                        'passport': handle_null(row[1]),
                        'income_date': row[2],
                        'outcome_date': handle_null(row[3]),
                        'active': discharged(row[3]),
                        'birth_date': row[4],
                        'name': ' '.join(row[5:7]),
                        'city': handle_null(row[7]),
                        'income_diag': handle_null(row[8]),
                        'outcome_diag': outcome_diag(row[9]),
                        'doctor': ' '.join(doctor_name),
                        'chamber': row[11],
                    }

                except (TypeError, IndexError) as e:
                    log.error(msg=f'Error occured: {e}')
                    continue

        return process_rows()

    def discharge_patient(self, patient_id: str) -> None:
        today = datetime.date.today().isoformat()
        DataModifier(self.SETTINGS, self.SQL).update_table('discharge-patient', today, patient_id)

    def create_appointment_record(self, appointment_data: dict) -> None:
        if appointment_data is None:
            log.error(f'Task creation aborted, the data is missing')
            return

        if not Validator.validate_appointment_data(appointment_data): 
            log.error(msg=f'Validation failed')
            return

        appointment_data = (
            appointment_data['asignee'], appointment_data['patient'],
            appointment_data.get('scheduled'), appointment_data.get('about')
        )

        DataModifier(self.SETTINGS, self.SQL).update_table('create-appointment-record', *appointment_data)
