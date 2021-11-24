import os
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import Blueprint, request, render_template

from app.policies import requires_login, requires_permission
from .hospital import HospitalController

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-hospital-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

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
    selected_doctor = request.values.get('doctor_selection')
    
    results = HospitalController().get_assigned_to_doctor(selected_doctor)

    if results is None: 
        log.warning(msg=f'Did not render bc results are empty!')
        return render_template('hospital_empty.j2')
    
    return render_template(
    'hospital_doctor_stats_results.j2',
    has_options=True,
    doctor=selected_doctor,
    options=results)

