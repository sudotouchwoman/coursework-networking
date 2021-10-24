'''
Routes of the base app.

Base app is created here and later blueprints are added to it via blueprint factory.

This module contains routes for main menu and something else, maybe
'''
from flask import (
    Flask,
    render_template,
    session)

from app.policies import requires_login, requires_permission

app = Flask(
    __name__,
    instance_relative_config=False,
    static_folder='static/',
    template_folder='templates/')

@app.errorhandler(404)
def page_not_found_redirect(e):
    return render_template('404.j2')

@app.route('/menu', methods=['GET', 'POST'])
def get_welcome_page() -> str:
    return render_template('app_welcome.j2')

@app.route('/exit', methods=['GET', 'POST'])
def get_exit_page() -> str:
    session.clear()
    return render_template('app_exit.j2')

@app.route('/hospital', methods=['GET', 'POST'])
@requires_login
@requires_permission
def get_hospital_menu():
    return render_template('hospital_menu.j2')

@app.route('/courses', methods=['GET', 'POST'])
@requires_login
@requires_permission
def get_courses_menu():
    return render_template('courses_menu.j2')