from flask import Flask, request, jsonify, render_template
import os
import datetime

APP = Flask(__name__, template_folder='../index/', static_folder='../static/')
HOST = os.getenv('HOST_NAME', None)
PORT = os.getenv('PORT', 5000)
DEBUG = bool(os.getenv('RUN_DEBUG', "True") == "True")
ENCODING = os.getenv('ENCODING', 'utf-8')
BASEDIR = os.getcwd()

@APP.route('/', methods= ['GET'])
def get_main_page() -> str:
    return 'This is main page'

@APP.route('/info', methods = ['GET'])
def get_info() -> str:
    PAGE = f'It s {datetime.datetime.now()}; Process ID {os.getpid()}'
    return PAGE

@APP.route('/home', methods=['GET'])
def get_home():
    return render_template('index.html')

@APP.route('/form', methods=['GET'])
def get_form():
    return render_template('form.html')


@APP.route('/dyn', methods=['GET'])
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

def run_app():
    APP.run(host=HOST, port=PORT, debug=DEBUG)