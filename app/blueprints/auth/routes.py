from flask import (
    Blueprint,
    request,
    session,
    render_template)

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from flask.helpers import url_for

from werkzeug.utils import redirect

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-auth-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='m', interval=10, backupCount=1)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

auth_bp = Blueprint(
    'auth_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        log.debug(msg=f'Redirects to login page')
        return render_template('login.j2')

    login = request.values.get('login')
    password = request.values.get('password')

    if login == 'admin' and password == 'admin':
        session['group_name'] = 'admin'
        log.info(msg=f'Admin logged in')
        return redirect(url_for('get_welcome_page'))

    if login == 'doctor' and password == 'doctor':
        session['group_name'] = 'doctor'
        log.info(msg=f'Doctor logged in')
        return redirect(url_for('get_welcome_page'))

    if login == 'teacher' and password == 'teacher':
        session['group_name'] = 'teacher'
        log.info(msg=f'Teacher logged in')
        return redirect(url_for('get_welcome_page'))

    log.info(msg=f'Encountered invalid credentials: {login}, {password}')
    return render_template('login.j2', login_error=True)
