from os import getenv
import logging
from logging.handlers import TimedRotatingFileHandler

from flask import (
    Blueprint,
    request,
    session,
    url_for,
    redirect,
    render_template)

from controller.auth import PolicyController

auth_view = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/auth.log')
auth_view.disabled = getenv('LOG_ON', "True") == "False"

auth_view.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
auth_view.addHandler(handler)

auth_bp = Blueprint(
    'auth_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        auth_view.info(msg=f'Redirects to login page')
        return render_template('login.j2')

    login = request.values.get('login')
    password = request.values.get('password')

    user_data = PolicyController().map_credentials(login=login, password=password)
    if user_data is None:
        auth_view.warning(msg=f'Encountered invalid credentials: {login}, {password}')
        return render_template('login.j2', login_error=True)

    session['group'] = user_data['group']
    session['id'] = user_data['id']
    session['name'] = user_data['name']
    session['group_name'] = user_data['group_name']
    
    auth_view.info(msg=f'{user_data["name"]} logged in')
    return redirect(url_for('main_menu'))


@auth_bp.route('/permission', methods=['GET'])
def permission():
    auth_view.warning(msg=f'Permission denied for user with id {session.get("id", "(unspecified id)")}')
    return render_template('permission.j2')
