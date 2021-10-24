from flask import Blueprint, request, jsonify, render_template
import logging
from logging.handlers import TimedRotatingFileHandler
import os

from app.content.courses import courses
from app.policies import requires_permission, requires_login

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-courses-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=1)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

courses_bp = Blueprint(
    'courses_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@courses_bp.route('/menu', methods=['GET'])
@requires_login
@requires_permission
def get_courses_menu():
    return render_template('courses_routes.j2')

@courses_bp.route('/request/services', methods=['POST'])
@requires_login
@requires_permission
def post_request_services():
    selected_lang = request.values.get('language_selection')
    selected_lang = 'All languages' if (selected_lang == '') else selected_lang
    
    results = courses.GLOBAL_COURSE_CONTROLLER.get_services_for_language(selected_lang)
    log.debug(msg=f'Controller response: {results}')
    
    if results[0]: return render_template(
        'services_results.j2',
        has_options=True,
        language=selected_lang,
        options=results[1])

    log.debug(msg=f'Did not render bc results are empty!')
    return render_template('services_results.j2', empty=True, language=selected_lang)

@courses_bp.route('/request/services', methods=['GET'])
@requires_login
@requires_permission
def get_request_services():
    return render_template('services_selection.html')

@courses_bp.route('/request/orders', methods=['POST'])
@requires_login
@requires_permission
def post_request_orders():
    selected_threshold = request.values.get('threshold')
    if selected_threshold == '': selected_threshold = '0'
    log.debug(msg=f'Selected threshold of {selected_threshold}')
    results = courses.GLOBAL_COURSE_CONTROLLER.get_orders_for_threshold(selected_threshold)
    log.debug(msg=f'Controller response: {results}')

    if results[0]: return render_template(
        'order_results.j2',
        has_options=True,
        threshold=selected_threshold,
        options=results[1]
    )

    log.debug(msg=f'Did not render bc results are empty!')
    return render_template('services_results.j2', empty=True, threshold=selected_threshold)


@courses_bp.route('/request/orders', methods=['GET'])
@requires_login
@requires_permission
def get_request_orders():
    return render_template('order_selection.html')