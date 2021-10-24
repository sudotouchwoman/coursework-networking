from flask import Blueprint, request, render_template
import logging
from logging.handlers import TimedRotatingFileHandler
import os

from app.content.hospital import hospital
from app.policies import requires_login, requires_permission

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

hospital_bp = Blueprint(
    'hospital_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@hospital_bp.route('menu', methods=['GET'])
@requires_login
@requires_permission
def get_hospital_menu():
    return render_template('hospital_routes.j2')

@hospital_bp.route('/request/department-stats', methods=['POST'])
@requires_login
@requires_permission
def post_request_department_stats():
    selected_department = request.values.get('department_selection')
    
    results = hospital.GLOBAL_HOSPITAL_CONTROLLER.get_departments_report(selected_department)
    log.debug(msg=f'Controller response: {results}')
    
    if results[0]: return render_template(
        'hospital_department_stats_results.j2',
        has_options=True,
        department=selected_department,
        options=results[1])

    log.warning(msg=f'Did not render bc results are empty!')
    return render_template('hospital_empty.j2')

@hospital_bp.route('/request/department-stats', methods=['GET'])
@requires_login
@requires_permission
def get_request_department_stats():
    departments = hospital.GLOBAL_HOSPITAL_CONTROLLER.get_department_list()
    log.debug(msg=f'Controller response: {departments}')

    if departments[0]:
        return render_template(
            'hospital_department_stats_selection.j2',
            has_options=departments[0],
            departments=departments[1])

    return render_template('hospital_empty.j2')

@hospital_bp.route('/request/doctor-stats', methods=['GET'])
@requires_login
@requires_permission
def get_request_doctor_stats():
    doctors = hospital.GLOBAL_HOSPITAL_CONTROLLER.get_doctors()
    log.debug(msg=f'Contoller response: {doctors}')

    if doctors[0]:
        return render_template(
            'hospital_doctor_stats_selection.j2',
            has_options=doctors[0],
            doctors=doctors[1])
    
    return render_template('hospital_empty.j2')

@hospital_bp.route('/request/doctor-stats', methods=['POST'])
@requires_login
@requires_permission
def post_request_doctor_stats():
    selected_doctor = request.values.get('doctor_selection')
    
    results = hospital.GLOBAL_HOSPITAL_CONTROLLER.get_assigned_to_doctor(selected_doctor)
    log.debug(msg=f'Controller response: {results}')

    if results[0]: return render_template(
        'hospital_doctor_stats_results.j2',
        has_options=True,
        doctor=selected_doctor,
        options=results[1])

    log.warning(msg=f'Did not render bc results are empty!')
    return render_template('hospital_empty.j2')
