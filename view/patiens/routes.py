from os import getenv
import logging
from logging.handlers import TimedRotatingFileHandler

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
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/log-patients-app-state.log')
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
    attributes = ('first_name', 'passport', 'second_name', 'attending_doctor', 'date_birth', 'chamber', 'city')
    new_patient_data = { attribute: request.values.get(attribute) for attribute in attributes }

    PatientController().create_patient_record(new_patient_data)
    return redirect(url_for('patients_bp.list_patients'))


@patients_bp.route('/list', methods=['POST', 'GET'])
@requires_login
@requires_permission
def list_patients():
    if request.method == 'GET':
        log.info(msg=f'Renders patient list')

        patients = PatientController().fetch_all_patients()
        doctors = HospitalController().get_doctors()
        chamber = HospitalController().check_chambers_capacity()

        if doctors is None or patients is None or chamber is None:
            log.warning(msg=f'Renders empty page as fetched data is empty')
            return render_template('hospital_empty.j2')

        return render_template(
            'patient_list.html',
            doctors=doctors,
            patients=patients,
            chambers_full=(chamber is None),
            optimal_chamber=chamber)

    to_discharge = request.values.get('patient_id')
    PatientController().discharge_patient(to_discharge)
    return redirect(url_for('patients_bp.list_patients'))
    

    
    

