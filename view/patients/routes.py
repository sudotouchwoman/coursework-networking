import json
from os import getenv
import logging
from logging.handlers import TimedRotatingFileHandler
from json import loads, dumps

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    session
)

from app.policies import requires_login, requires_permission
from controller.hospital import HospitalController
from controller.patients import PatientController

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

patients_bp = Blueprint(
    'patients_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@patients_bp.route('menu', methods=['GET'])
@requires_login
@requires_permission
def menu():
    log.info(msg=f'Renders menu page')
    return render_template('patient_menu.html')


@patients_bp.route('/add', methods=['POST'])
@requires_login
@requires_permission
def add_new_patient():
    attributes = ('first_name', 'passport', 'second_name', 'date_birth', 'city', 'initial_diagnosis')
    new_patient_data = { attribute: request.values.get(attribute) for attribute in attributes }

    PatientController().create_patient_record(new_patient_data)
    return redirect(url_for('.list_patients'))


@patients_bp.route('/list', methods=['POST', 'GET'])
@requires_login
@requires_permission
def list_patients():
    log.info(msg=f'Renders patient list')

    patients = PatientController().fetch_unassigned()

    if patients is None:
        log.warning(msg=f'Renders empty page bc fetched data is empty')
        return render_template('hospital_empty.j2')
    
    if request.method == 'GET':
        
        if 'assign_response' not in request.values:
                return render_template(
                'patient_list.j2',
                patients=patients)

        assign_response = loads(request.values['assign_response'])

        return render_template(
            'patient_list.j2',
            patients=patients,
            has_response=True,
            assign_response=assign_response)

    departments = HospitalController().get_department_list()
    patient = request.values.get('patient_id')
    patient = PatientController().find_patient(patient)

    return render_template(
        'patient_list.j2',
        has_departments=True,
        departments=departments,
        detailed_patient_data=patient,
        patients=patients)


@patients_bp.route('/assign', methods=['POST'])
@requires_login
@requires_permission
def assign_to_department():
    to_assign = request.values.get('patient_id')
    where_to_assign = request.values.get('department_id')

    assign_response = PatientController().assign_patient(to_assign, where_to_assign)
    return redirect(url_for('.list_patients', assign_response=dumps(assign_response)))