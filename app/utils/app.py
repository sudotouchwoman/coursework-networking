from flask import Flask, request, jsonify, render_template
import os
import datetime
from .config import DevConfig

app = Flask(__name__, template_folder='templates/', static_folder='static/')

@app.route('/', methods= ['GET'])
def get_main_page() -> str:
    return 'This is main page'

@app.route('/info', methods = ['GET'])
def get_info() -> str:
    PAGE = f'It s {datetime.datetime.now()}; Process ID {os.getpid()}'
    return PAGE

@app.route('/home', methods=['GET'])
def get_home():
    return render_template('index.html')

@app.route('/form', methods=['GET'])
def get_form():
    return render_template('form.html')

@app.route('/ex', methods=['GET'])
def get_ex():
    return render_template('ex.html')

@app.route('/dyn', methods=['GET'])
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
    CONFIG = DevConfig()
    app.run(host=CONFIG.HOST, port=CONFIG.PORT, debug=CONFIG.DEBUG)