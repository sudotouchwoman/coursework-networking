from os import getenv
from json import loads
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import (
    Blueprint,
    request,
    render_template,
    session
)
from flask.helpers import url_for
from werkzeug.utils import redirect

from app.policies import requires_login, requires_permission
from controller.hospital import HospitalController

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

hospital_bp = Blueprint(
    'hospital_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@hospital_bp.route('menu', methods=['GET'])
@requires_login
@requires_permission
def get_hospital_menu():
    log.info(msg=f'Renders hospital menu page')
    return render_template('hospital_routes.j2')


@hospital_bp.route('/request/department-stats', methods=['POST'])
@requires_login
@requires_permission
def post_request_department_stats():
    selected_department = request.values.get('department_selection')
    
    results = HospitalController().get_departments_report(selected_department)
    
    if results is None:
        log.warning(msg=f'Did not render bc results are empty!')
        return render_template('hospital_empty.j2')

    return render_template(
        'hospital_department_stats_results.j2',
        has_options=True,
        department=selected_department,
        options=results)


@hospital_bp.route('/request/department-stats', methods=['GET'])
@requires_login
@requires_permission
def get_request_department_stats():
    log.info(msg=f'Renders departments page')
    departments = HospitalController().get_department_list()

    if departments is None:
        log.warning(msg=f'Renders empty page as fetched data is empty')
        return render_template('hospital_empty.j2')

    return render_template(
        'hospital_department_stats_selection.j2',
        has_options=True,
        departments=departments)


@hospital_bp.route('/request/doctor-stats', methods=['GET'])
@requires_login
@requires_permission
def get_request_doctor_stats():
    log.info(msg=f'Renders doctors page')
    doctors = HospitalController().get_doctors()

    if doctors is None:    
        log.warning(msg=f'Renders empty page as fetched data is empty')
        return render_template('hospital_empty.j2')
    
    return render_template(
        'hospital_doctor_stats_selection.j2',
        has_options=True,
        doctors=doctors)


@hospital_bp.route('/request/doctor-stats', methods=['POST'])
@requires_login
@requires_permission
def post_request_doctor_stats():
    selected_doctor = (request.values.get('doctor_selection'))
    selected_doctor = loads(selected_doctor)
    id = selected_doctor.get('id')
    name = selected_doctor.get('name')

    results = HospitalController().get_assigned_to_doctor(id)
    if results is None: 
        log.warning(msg=f'Did not render bc results are empty!')
        return render_template('hospital_empty.j2')
    
    return render_template(
    'hospital_doctor_stats_results.j2',
    has_options=True,
    doctor=name,
    options=results)


@hospital_bp.route('/appointments', methods=['GET', 'POST'])
@requires_login
@requires_permission
def list_appointments():
    if request.method == 'GET':
        doctor_id = session['id']
        appointments = HospitalController().filter_appointments(by='doctor', value=doctor_id)

        if appointments is None: return render_template('appointment_list.j2')

        return render_template(
            'appointment_list.j2',
            appointments=appointments
        )

    if 'action' not in request.values.keys(): return render_template('hospital_empty.j2')
    if 'appointment_id' not in request.values.keys(): return render_template('hospital_empty.j2')

    HospitalController().update_appointment(request.values['action'], request.values['appointment_id'])
    return redirect(url_for('hospital_bp.list_appointments'))
        
