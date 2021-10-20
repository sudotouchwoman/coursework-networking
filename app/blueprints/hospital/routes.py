from flask import Blueprint, request, jsonify, render_template
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

from app.content.hospital import hospital
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

hospital_bp = Blueprint(
    'hospital_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@hospital_bp.route('menu', methods=['GET'])
def get_hospital_menu():
    return render_template('hospital_routes.j2')

@hospital_bp.route('/request/department-stats', methods=['POST'])
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
    return render_template('hospital_empty.j2', empty=True, department=selected_department)

@hospital_bp.route('/request/department-stats', methods=['GET'])
def get_request_department_stats():
    departments = hospital.GLOBAL_HOSPITAL_CONTROLLER.get_department_list()
    log.debug(msg=f'Controller response: {departments}')

    return render_template(
        'hospital_department_stats_selection.j2',
        has_options=departments[0],
        departments=departments[1])

# @hospital_bp.route('/request/orders', methods=['POST'])
# def post_request_orders():
#     selected_threshold = request.values.get('threshold')
#     results = courses.GLOBAL_COURSE_CONTROLLER.get_orders_for_threshold(selected_threshold)
#     log.debug(msg=f'Controller response: {results}')

#     if results[0]: return render_template(
#         'order_results.j2',
#         has_options=True,
#         threshold=selected_threshold,
#         options=results[1]
#     )

#     log.debug(msg=f'Did not render bc results are empty!')
#     return render_template('services_results.j2', empty=True, threshold=selected_threshold)


# @hospital_bp.route('/request/orders', methods=['GET'])
# def get_request_orders():
#     return render_template('order_selection.html')