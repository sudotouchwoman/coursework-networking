from flask import Blueprint, request, jsonify, render_template
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

from app.process import courses
log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('DB_LOGFILE_NAME', 'logs/log-courses-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=1)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info(msg=f'LOG STARTED: [{datetime.datetime.now(tz=None)}]')

user_bp = Blueprint(
    'user_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@user_bp.route('/request/services', methods=['POST'])
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

@user_bp.route('/request/services', methods=['GET'])
def get_request_services():
    return render_template('services_selection.html')

@user_bp.route('/request/orders', methods=['POST'])
def post_request_orders():
    selected_threshold = request.values.get('threshold')
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


@user_bp.route('/request/orders', methods=['GET'])
def get_request_orders():
    return render_template('order_selection.html')