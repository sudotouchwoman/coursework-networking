from flask import Blueprint, request, jsonify, render_template
import os
import datetime
from app.database import query

user_bp = Blueprint(
    'user_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@user_bp.route('/', methods= ['GET'])
def get_root() -> str:
    return 'This is main page for user scenario. Check out /getuser, /createuser'

@user_bp.route('/auth', methods = ['GET'])
def get_auth() -> str:
    return render_template('home.html')

@user_bp.route('/auth', methods = ['POST'])
def post_auth() -> str:
    db_settings = query.load_db_config('db-config.json')
    results = query.SelectQuery(db_settings).execute_query(
        ['id_patient', 'firstname', 'secondname', 'attending_doctor'],
        'patient', limit=request.values.get('patient_limit'))

    if results is None: return render_template('auth.html', message=False, success=False, empty=True)
    return render_template('auth.html', message=True, success=True, table_content=results)

@user_bp.route('/home', methods=['GET'])
def get_user_bp():
    return render_template('home.html')

@user_bp.route('/form', methods=['GET'])
def get_form():
    return render_template('form.html')

@user_bp.route('/main', methods=['GET'])
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
