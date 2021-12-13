'''
Business-process related to patients: add new patient, assign to doctor etc
'''
from os import getenv, initgroups
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

        self.MODIFIER = DataModifier(db_settings, sql_dir)
        self.SOURCE = DataSource(db_settings, sql_dir)


    def create_patient_record(self, patient_data: dict) -> None:
        if patient_data is None:
            log.error(f'Patient creation aborted, the data is missing')
            return

        if not Validator.validate_patient_data(patient_data): 
            log.error(msg=f'Validation failed')
            return

        patient_data = (
            patient_data['passport'], datetime.date.today().isoformat(),
            patient_data['date_birth'], patient_data['first_name'],
            patient_data['second_name'], patient_data['city'],
            patient_data['initial_diagnosis']
        )

        self.MODIFIER.update_table('create-patient-record', *patient_data)


    def find_patient(self, patient_id: int) -> dict or None:
        try:
            patient_data = list(self.SOURCE.fetch_results('fetch-patient-byid', patient_id))[0]
            handle_null = lambda s: 'N/A' if s is None or not s else s

            return {
                'id': patient_data[0],
                'passport': handle_null(patient_data[1]),
                'birth_date': handle_null(patient_data[4]),
                'awaiting': f'{(datetime.date.today() - patient_data[2]).days} days',
                'name': ' '.join(patient_data[5:7]),
                'city': handle_null(patient_data[7]),
                'income_diag': handle_null(patient_data[8]),
            }

        except (TypeError, IndexError) as e:
            log.error(msg=f'Error during patient lookup: {e}. Patient id = {patient_id}')
            return


    def fetch_all_patients(self) -> None or tuple:
        log.debug(msg=f'Fetches patient list')

        patients = self.SOURCE.fetch_results('fetch-patients')

        if patients is None:
            log.warning(msg=f'Failed to fetch patients. Is SQL Server running?')
            return

        handle_null = lambda s: 'N/A' if s is None or not s else s

        def process_rows():
            for i, row in enumerate(patients, start=1):
                    yield {
                        'num': i,
                        'id': row[0],
                        'passport': handle_null(row[1]),
                        'name': ' '.join(row[2:4]),
                        'birth_date': handle_null(row[4]),
                        'income_date': handle_null(row[5]),
                        'outcome_date': handle_null(row[6]),
                        'income_diag': handle_null(row[7]),
                        'outcome_diag': handle_null(row[8]),
                        'city': handle_null(row[9]),
                        'chamber': handle_null(row[10]),
                        'attending_doctor': ' '.join(row[11:13]),
                        'id_doctor': row[13]
                    }

        return process_rows()


    def discharge_patient(self, patient_id: int) -> None:
        today = datetime.date.today().isoformat()
        self.MODIFIER.update_table('discharge-patient', today, patient_id)


    def fetch_unassigned(self) -> None or tuple:
        log.debug(msg=f'Fetches unassigned patients')

        patients = self.SOURCE.fetch_results('fetch-newcome-patients')

        if patients is None:
            log.warning(msg=f'Failed to fetch patients. Is SQL Server running?')
            return

        handle_null = lambda s: 'N/A' if s is None or not s else s

        def process_rows():
            for i, row in enumerate(patients, start=1):
                    yield {
                        'num': i,
                        'id': row[0],
                        'passport': handle_null(row[1]),
                        'income_date': handle_null(row[2]),
                        'birth_date': handle_null(row[3]),
                        'name': ' '.join(row[4:6]),
                        'city': handle_null(row[6]),
                        'income_diag': handle_null(row[7]),
                    }

        return process_rows()

    def assign_patient(self, patient_id: int, department_id: int) -> dict or None:
        optimal_doctor = self.SOURCE.fetch_results('select-least-loaded', department_id)
        optimal_chamber = self.SOURCE.fetch_results('check-chambers', department_id)

        if optimal_chamber is None or optimal_doctor is None:
            # there was not found any matching chamber/doctor
            log.error(msg=f'Did not found matching doctor/chamber')
            return

        try:
            # extract the first row and unpack it
            optimal_chamber = list(optimal_chamber)[0]
            optimal_doctor = list(optimal_doctor)[0]

            optimal_chamber = optimal_chamber[0]
            optimal_doctor, *doctor_initials = optimal_doctor
        
        except (TypeError, IndexError) as e:
            log.error(msg=f'Error occured while best doctor/chamber lookup: {e}')
            return

        # modify all tables
        self.MODIFIER.update_table('assign-to-doctor', optimal_doctor, optimal_chamber, patient_id)
        # self.MODIFIER.update_table('add-patient', optimal_doctor)
        # self.MODIFIER.update_table('update-chamber', optimal_chamber)

        log.debug(msg=f'Updated table: assigned {patient_id} to {optimal_doctor} ({doctor_initials}), chamber is {optimal_chamber}')
        return {
                'attending_doctor': ' '.join(doctor_initials),
                'chamber': optimal_chamber
            }


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

        self.MODIFIER.update_table('create-appointment-record', *appointment_data)
