from flask import Blueprint, request, jsonify, render_template
import os
import datetime
from ...database import query


home_bp = Blueprint(
    'home_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@home_bp.route('/', methods= ['GET'])
def get_main_page() -> str:
    return 'This is main page. Check out /dyn, /home and /info'

@home_bp.route('/info', methods = ['GET'])
def get_info() -> str:
    PAGE = f'It s {datetime.datetime.now()}; Process ID {os.getpid()}'
    return PAGE

@home_bp.route('/home', methods=['GET'])
def get_home_bp():
    return render_template('index.html')

@home_bp.route('/form', methods=['GET'])
def get_form():
    return render_template('form.html')

@home_bp.route('/main', methods=['GET'])
def get_dynamic_page():
    PARAMS = {
        'username':'sakeof',
        'list':[
            'boo',
            'ba',
            'sus'
        ]
    }
    return render_template('main.html', **PARAMS)

@home_bp.route('/db-connect', methods= ['GET'])
def get_db_info():
    db_settings = query.load_db_config('db-config.json')
    results = query.SelectQuery(db_settings).execute_query(['id_patient', 'firstname', 'secondname', 'attending_doctor'], 'patient')
    PARAMS = {
        'username':'sakeof',
        'list':[
            'boo',
            'ba',
            'sus'
        ]
    }
    if results is None: return render_template('db.html', message=False, success=False, empty=True, **PARAMS)
    return render_template('db.html', message=True, success=True, table_content=results, **PARAMS)
