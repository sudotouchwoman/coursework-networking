'''
Business-process related to patients: add new patient, assign to doctor etc
'''
import datetime
from flask import current_app
from schema import *

from app import make_logger
from database.ORM import DataSource, DataModifier
from . import Validator

patients_log = make_logger(__name__, 'logs/patients.log')

DB_CONFIG = current_app.config['DB'].get('hospital')
SQL_DIR = current_app.config.get('QUERIES')

class PatientController:
    '''Controller for patient routines.
    The methods contain patient creation, assignment and discharging.
    The system is also capable of appointment creation for attending doctors
    '''

    def __init__(self, db_settings: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if db_settings is None or sql_dir is None:
            patients_log.fatal(msg=f'Recieved this: {db_settings} and {sql_dir}')
            patients_log.fatal(msg=f'Failed to create Hospital controller! Is `hospital` in db config?')
            raise TypeError('Failed to create Hospital  controller')

        self.MODIFIER = DataModifier(db_settings, sql_dir)
        self.SOURCE = DataSource(db_settings, sql_dir)


    def create_patient_record(self, patient_data: dict) -> bool:
        '''Creates new record in `patient` table.
        The data is validated before inserting.

        Args:
        + `patient_data`: dict containing data to insert into table, should contain the following keys:
            * `first_name`: `str`
            * `second_name`: `str`
            * `initial_diag`: `str`
            * `passport`: `str` or `None`
            * `date_birth`: iso-formatted date `str`
            * `city`: `str`

        Returns: `None`
            '''

        patients_log.debug(msg=f'Creates new patient record')
        if patient_data is None:
            patients_log.error(f'Patient creation aborted, the data is missing')
            return False

        if not Validator.validate_patient_data(patient_data): 
            patients_log.error(msg=f'Validation failed')
            return False

        patient_data = (
            patient_data['passport'], datetime.date.today().isoformat(),
            patient_data['date_birth'], patient_data['first_name'],
            patient_data['second_name'], patient_data['city'],
            patient_data['initial_diagnosis']
        )

        self.MODIFIER.update_table('create-patient-record', *patient_data)
        patients_log.info(msg=f'Created new patient record')
        return True


    def find_patient(self, patient_id: int) -> dict or None:
        '''Looks for record in `patient` table with given `patient_id` primary key.
        return the formatted `dict` if successfully, `None` otherwise.
        
        Args:

        + `patient_id`: `int`

        Returns: `None` or `dict`
            '''

        patients_log.debug(msg=f'Patient lookup with id {patient_id}')
        try:
            patient_data = list(self.SOURCE.fetch_results('fetch-patient-byid', patient_id))[0]
            handle_null = lambda s: s if s else 'N/A'

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
            patients_log.error(msg=f'Error during patient lookup: {e}. Patient id = {patient_id}')
            return


    def fetch_all_patients(self) -> None or tuple:
        '''
        Fetch all records from `patient` table. Return `None` if error occurs,
        generator is returned otherwise. Each generator item is `dict` of
        patient properties to be parsed during template building.

        Returns: `None` or `Iterable[dict[str, Any]]`
        '''

        patients_log.debug(msg=f'Fetches patient list')

        patients = self.SOURCE.fetch_results('fetch-patients')

        if patients is None:
            patients_log.warning(msg=f'Failed to fetch patients. Is SQL Server running?')
            return

        handle_null = lambda s: s if s else 'N/A'

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

        patients_log.info(msg=f'Fetched patient list')
        return process_rows()

    
    def fetch_dischargable_patients(self) -> None or tuple:
        patients_log.debug(msg=f'Fetches list of dischargable patients')

        patients = self.SOURCE.fetch_results('fetch-dischargable')

        if patients is None:
            patients_log.warning(msg=f'Failed to fetch patients. Is SQL Server running?')
            return

        handle_null = lambda s: s if s else 'N/A'

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
                        'outcome_diag': handle_null(row[8]),

                        'id_doctor': row[9],
                        'chamber': handle_null(row[10]),
                        'attending_doctor': ' '.join(row[11:13]),
                    }

        patients_log.info(msg=f'Fetched dischargable list')
        return process_rows()


    def discharge_patient(self, patient_id: int, doctor_id: int, chamber_id: int) -> None:
        '''Discharge patient, i.e. set the `outcome_date` column value to today.

        Args:

        * `patient_id`: `int`, primary key of the patient record to be updated

        Returns: `None`
        '''

        today = datetime.date.today().isoformat()

        self.MODIFIER.update_table('discharge-patient', today, patient_id)
        self.MODIFIER.update_table('release-chamber', chamber_id)
        self.MODIFIER.update_table('release-doctor', doctor_id)

        patients_log.info(msg=f'Released reources: chamber with id {chamber_id} and doctor with id {doctor_id}')
        patients_log.info(msg=f'Discharged patient with id {patient_id}')


    def fetch_unassigned(self) -> None or tuple:
        '''Fetch all patients who do not habe an attending doctor.
        Simular to `fetch_all_patients()`. Return `None` if there was an error during
        processing and generator expression otherwise.

        Returns: `None` or `Iterable[dict[str, Any]]`
        '''

        patients_log.debug(msg=f'Fetches unassigned patients')

        patients = self.SOURCE.fetch_results('fetch-newcome-patients')

        if patients is None:
            patients_log.warning(msg=f'Failed to fetch patients. Is SQL Server running?')
            return

        handle_null = lambda s: s if s else 'N/A'

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

        patients_log.info(msg=f'Fetched unassigned patients')
        return process_rows()


    def assign_patient(self, patient_id: int, department_id: int) -> dict or None:
        '''Try to assign given patient to the provided `department_id`. This said, matching
        doctor and chamber with free space should be found. First, try to find doctor and chamber
        according to the rules specified in sql queries `select-least-loaded` and `check-chambers`.
        
        The former looks for a doctor working at given department with least assigned patients
        and the latter looks for a chamber with most free space.

        If the procedure is successful (this said, optimal doctor and chamber were found), return `dict`
        containing attending doctor initials and chamber id.

        After successful assignment the system would automatically create new appointment for
        the newcome patient. This will appear in the corresponding section in doctor UI

        Args:

        * `patient_id`: int, patient to assign
        * `department_id`: int, department to assign to

        Returns: `None` or `dict[str, [int, str]]`
        '''

        patients_log.debug(msg=f'Starts assignment procedure, patient {patient_id}, department {department_id}')

        optimal_doctor = self.SOURCE.fetch_results('select-least-loaded', department_id)
        optimal_chamber = self.SOURCE.fetch_results('check-chambers', department_id)

        if optimal_chamber is None or optimal_doctor is None:
            # No matching chamber/doctor found
            patients_log.error(msg=f'Did not found matching doctor/chamber')
            return

        try:
            # extract the first row and unpack it
            optimal_chamber = list(optimal_chamber)[0]
            optimal_doctor = list(optimal_doctor)[0]

            optimal_chamber = optimal_chamber[0]
            optimal_doctor, *doctor_initials = optimal_doctor
        
        except (TypeError, IndexError) as e:
            patients_log.error(msg=f'Error occured during best doctor/chamber lookup: {e}')
            return

        # modify all tables
        # should be uncommented to remove debug
        self.MODIFIER.update_table('assign-to-doctor', optimal_doctor, optimal_chamber, patient_id)
        self.MODIFIER.update_table('occupy-doctor', optimal_doctor)
        self.MODIFIER.update_table('occupy-chamber', optimal_chamber)

        patients_log.info(msg=f'Updated table: assigned {patient_id} to {optimal_doctor} ({doctor_initials}), chamber is {optimal_chamber}')
        
        new_appointment_data = {
            'assignee': str(optimal_doctor),
            'patient': str(patient_id),
            'about': 'Первичный прием',
            'scheduled': datetime.datetime.today() + datetime.timedelta(days=1)
        }

        self.create_appointment_record(new_appointment_data)
        
        return {
                'attending_doctor': ' '.join(doctor_initials),
                'chamber': optimal_chamber
            }


    def create_appointment_record(self, appointment_data: dict) -> None:
        '''Create new record in `appointment` table. Validate the provided
        data before inserting

        Args:

        * `appointment_data`: `dict`, should contain the following keys:
            * `assignee`: `str`, doctor id
            * `patient`: `str`, patient id
            * `about` (optional): `str`
            * `scheduled` (optional): `datetime`

        Returns: `None`
        '''
        patients_log.debug(msg=f'Creates new doctor task record')

        if appointment_data is None:
            patients_log.error(f'Task creation aborted, the data is missing')
            return

        if not Validator.validate_appointment_data(appointment_data): 
            patients_log.error(msg=f'Validation failed')
            return

        appointment_data = (
            appointment_data['assignee'], appointment_data['patient'],
            appointment_data.get('scheduled'), appointment_data.get('about')
        )

        self.MODIFIER.update_table('create-appointment-record', *appointment_data)
        patients_log.info(msg=f'Created new task record')
