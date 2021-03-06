'''
Business-process for hospital (yet in a single module)
'''
import datetime

from flask import current_app

from database.ORM import DataSource, DataModifier
from app import make_logger
from . import Validator

hospital_log = make_logger(__name__, 'logs/hospital.log')

DB_CONFIG = current_app.config['DB'].get('hospital')
SQL_DIR = current_app.config.get('QUERIES')

class HospitalController:

    def __init__(self, db_settings: dict = DB_CONFIG, sql_dir: str = SQL_DIR) -> None:
        if db_settings is None or sql_dir is None:
            hospital_log.fatal(msg=f'Recieved this: {db_settings} and {sql_dir}')
            hospital_log.fatal(msg=f'Failed to create Hospital controller! Is `hospital` in db config?')
            raise TypeError('Failed to create Hospital controller')
        
        self.SOURCE = DataSource(db_settings, sql_dir)
        self.MODIFIER = DataModifier(db_settings, sql_dir)


    def get_department_list(self) -> None or tuple:
        # candidate for caching
        hospital_log.debug(msg=f'Fetches department list')
        selected = self.SOURCE.fetch_results('department-list')

        if selected is None:
            hospital_log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return

        def process_rows():
            for row in selected:
                yield {
                    'id': row[0],
                    'title': row[1]
                }

        hospital_log.info(msg=f'Fetched department list')
        return process_rows()


    def make_department_report(self, department_id: int, department_name: str = 'N/A') -> None or tuple:
        hospital_log.debug(msg=f'Produces report for selected department {department_id}')

        chambers_info = self.SOURCE.fetch_results('department-report', department_id)
        doctors_info = self.SOURCE.fetch_results('department-doctors', department_id)

        if not chambers_info or not doctors_info:
            hospital_log.error(msg=f'Failed to create report:\
             is SQL server running? See db logs for more detailed info')
            return

        department_head = self.SOURCE.fetch_results('department-head', department_id)

        try:
            department_head = list(department_head)[0]
        except (TypeError, IndexError):
            hospital_log.error(msg=f'Error occured while obtaining\
                initials of department head. Make sure the query is OK')
            department_head = 'N/A'

        def process_chambers():
            for i, row in enumerate(chambers_info, start=1):
                try:
                    yield {
                        'num': i,
                        'class': row[0],
                        'capacity': row[1],
                        'occupied': row[2],
                    }

                except IndexError:
                    hospital_log.warning(msg=f'Index error while making department report\
                        make sure the SQL query is correct')
                    continue

        def process_doctors():
            for i, row in enumerate(doctors_info, start=1):
                try:
                    yield {
                        'num': i,
                        'id': row[0],
                        'name': ' '.join(row[1:3]),
                        'assigned': row[3]
                    }
                
                except IndexError:
                    hospital_log.warning(msg=f'Index error while making department report')
                    continue

        return {
            'title': department_name,
            'head': ' '.join(department_head),
            'chambers': process_chambers(),
            'doctors': process_doctors()
        }


    def get_doctors(self) -> None or tuple:
        # also condidate for caching
        hospital_log.debug(msg=f'Fetches list of doctors')
        selected = self.SOURCE.fetch_results('select-doctorlist')

        if not selected:
            hospital_log.error(msg=f'Failed to fetch: is SQL server running? See db logs for more detailed info')
            return

        def process_rows():
            for row in selected:
                yield {
                    'id': row[0],
                    'name': ' '.join(row[1:])
                    }

        hospital_log.debug(msg=f'Fetched list of doctors')
        return process_rows()


    def get_assigned_to_doctor(self, doctor) -> None or tuple:

        hospital_log.debug(msg=f'Collects assignees for {doctor}')
        selected = self.SOURCE.fetch_results('fetch-patients-filterby-doctor', doctor)

        if not selected:
            hospital_log.warning(msg=f'Failed to create report: looks like we encountered fantom doctor with credentials {doctor}')
            return

        handle_null = lambda s: '???? ??????????????' if s is None or not s else s

        def process_rows():
            for i, row in enumerate(selected, start=1):
                yield {
                    'num': i,
                    'name': ' '.join(row[0:2]),
                    'diagnosis': handle_null(row[2]),
                    'chamber': row[3],
                    'duration': f'{(datetime.date.today() - row[4]).days} days',
                    'date_birth': row[5],
                    'recovered': row[6] is not None
                }

        hospital_log.debug(msg=f'Successfully fetched report for given doctor')
        return process_rows()


    def get_doctor_name(self, id_doctor: int) -> str or None:
        name = self.SOURCE.fetch_results('select-doctor-initials', id_doctor)
        return ' '.join(name[0]) if name else None


    def check_chambers_capacity(self) -> int or None:
        hospital_log.debug(msg=f'Checks capacity of chambers')

        chamber_data = self.SOURCE.fetch_results('check-chambers')
        try:
            chamber_data = list(chamber_data)[0]
        except IndexError:
            hospital_log.warning(msg=f'Chambers must be full')
            return
        except TypeError:
            hospital_log.error(msg=f'Error occured during db connection')
            return

        hospital_log.debug(msg=f'Chamber {chamber_data[0]} is the biggest chamber with free space')
        return chamber_data[0]

    
    def filter_appointments(self, by: str, value: str) -> None or tuple:
        options = {
            'doctor': 'fetch-appointments-filterby-doctor',
            'patient': 'fetch-appointments-filterby-patient',
            'status': 'fetch-appointments-filterby-status'
        }

        if by not in options.keys():
            hospital_log.error(msg=f'Invalid filter: {by}')
            return

        filtered = self.SOURCE.fetch_results(options[by], value)

        if not filtered:
            hospital_log.warning(msg=f'Failed to fetch appointments satisfying {by}={value}')
            return

        handle_null = lambda s: s if s else 'N/A'

        def handle_status_code(s: int) -> str:
            if s == 0: return u'?????????? ????????????'
            if s == 1: return u'????????????'
            if s == 2: return u'????????????????'
            if s == 3: return u'????????????????'
            return '?????????????????????? ????????????'


        def process_rows():
            for i, row in enumerate(filtered, start=1):
                try:
                    initials = self.SOURCE\
                        .fetch_results('fetch-patient-byid', row[2])
                    initials = list(initials)[0]
                    yield {
                        'num': i,
                        'id': row[0],
                        'assignee': row[1],
                        'patient_id': row[2],
                        'patient': ' '.join(initials[5:7]),
                        'about': handle_null(row[4]),
                        'scheduled': handle_null(row[3]),
                        'status': handle_status_code(row[5]),
                        'status_code': row[5]
                    }
                except (TypeError, IndexError):
                    hospital_log.warning(msg=f'Exception occured while processing row: {row}')
                    yield {
                        'num': i,
                        'id': row[0],
                        'assignee': row[1],
                        'patient_id': row[2],
                        'patient': 'N/A',
                        'about': handle_null(row[4]),
                        'scheduled': handle_null(row[3]),
                        'status': handle_status_code(row[5]),
                        'status_code': row[5]
                    }

        hospital_log.info(msg=f'Successfully fetched appointments')
        return process_rows()


    def update_appointment(self, action: str, appointment_id) -> None:
        hospital_log.debug(msg=f'Updates appointment status')
        options = {
            'complete': 3,
            'accept': 1,
            'reject': 2
            }

        if action not in options.keys():
            hospital_log.error(msg=f'Invalid action: {action}')
            return

        self.MODIFIER\
            .update_table('update-appointment', options[action], appointment_id)


    def schedule_appointment(self, context: dict) -> None:
        hospital_log.debug(msg=f'Schedules appointment')

        if not Validator.validate_appointment_schedule(context):
            hospital_log.error(msg=f'Failed to schedule appointment: validation not passed: {context}')
            return

        is_final, schedule_to = context['is_final'],context['schedule_to']
        comment, appointment_id = context['about'], context['appointment_id']
        patient_id = context['patient_id']


        if is_final:
            self.MODIFIER.update_table('set-diagnosis', comment, patient_id)
            self.update_appointment('complete', appointment_id)
            hospital_log.info(msg=f'Have set final diagnosis to {patient_id}')
            return

        if not schedule_to: schedule_to = \
            datetime.datetime.today() + datetime.timedelta(weeks=1)
        else:
            schedule_to = datetime.datetime.strptime(schedule_to, '%Y-%m-%dT%H:%M')

        self.MODIFIER.update_table('schedule-appointment', comment, schedule_to, appointment_id)
        hospital_log.info(msg=f'Scheduled {appointment_id} to {schedule_to}')
