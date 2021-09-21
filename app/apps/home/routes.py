from flask import Blueprint, request, jsonify, render_template
import os
import datetime

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

@home_bp.route('/dyn', methods=['GET'])
def get_dynamic_page():
    PARAMS = {
        'username':'sakeof',
        'list':[
            'boo',
            'ba',
            'sus'
        ]
    }
    return render_template('dynamic.html', **PARAMS)