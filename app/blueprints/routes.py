'''
Routes of the base app.

Base app is created here and later blueprints are added to it via blueprint factory.

This module contains routes for main menu and something else, maybe
'''
from flask import Flask, render_template

app = Flask(
    __name__,
    instance_relative_config=False,
    static_folder='static/',
    template_folder='templates/')

@app.errorhandler(404)
def page_not_found_redirect(e):
    return render_template('404.j2')

@app.route('/menu', methods= ['GET'])
def get_main_page() -> str:
    return 'This is main page. Check out /home/.. and /user/.. blueprints'
