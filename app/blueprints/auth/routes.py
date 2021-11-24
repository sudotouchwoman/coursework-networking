from flask import (
    Blueprint,
    request,
    session,
    url_for,
    redirect,
    render_template)

import logging
from logging.handlers import TimedRotatingFileHandler
import os

from .auth import GLOBAL_ROLE_CONTROLLER

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-auth-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
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

    role_name = GLOBAL_ROLE_CONTROLLER.get_group_name(login=login, password=password)
    if role_name is None:
        log.info(msg=f'Encountered invalid credentials: {login}, {password}')
        return render_template('login.j2', login_error=True)

    session['group_name'] = role_name
    log.info(msg=f'{role_name} logged in')
    return redirect(url_for('get_welcome_page'))

