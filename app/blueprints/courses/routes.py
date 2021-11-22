import os
import logging
from logging.handlers import TimedRotatingFileHandler

from werkzeug.utils import redirect
from flask import (
    Blueprint, request,
    jsonify, render_template,
    url_for, session)

from app.content.courses import courses
from app.policies import requires_permission, requires_login
from .cart import delete_from_cart, add_to_cart, get_cart

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = os.getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = os.getenv('APP_LOGFILE_NAME', 'logs/log-courses-app-state.log')
log.disabled = os.getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

courses_bp = Blueprint(
    'courses_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@courses_bp.route('/menu', methods=['GET'])
@requires_login
@requires_permission
def get_courses_menu():
    log.info(msg=f'Renders courses menu page')
    return render_template('courses_routes.j2')


@courses_bp.route('/request/services', methods=['POST'])
@requires_login
@requires_permission
def post_request_services():
    selected_lang = request.values.get('language_selection')
    selected_lang = 'All languages' if (selected_lang == '') else selected_lang
    log.debug(msg=f'Collected language: {selected_lang}')
    
    results = courses.GLOBAL_COURSE_CONTROLLER.get_services_for_language(selected_lang)
    
    if results[0]: return render_template(
        'services_results.j2',
        has_options=True,
        language=selected_lang,
        options=results[1])

    log.warning(msg=f'Did not render bc results are empty!')
    return render_template('services_results.j2', empty=True, language=selected_lang)


@courses_bp.route('/request/services', methods=['GET'])
@requires_login
@requires_permission
def get_request_services():
    log.info(msg=f'Renders service selection page')
    return render_template('services_selection.html')


@courses_bp.route('/request/orders', methods=['POST'])
@requires_login
@requires_permission
def post_request_orders():
    selected_threshold = request.values.get('threshold')
    if selected_threshold == '': selected_threshold = '0'
    log.debug(msg=f'Selected threshold of {selected_threshold}')
    results = courses.GLOBAL_COURSE_CONTROLLER.get_orders_for_threshold(selected_threshold)

    if results[0]: return render_template(
        'order_results.j2',
        has_options=True,
        threshold=selected_threshold,
        options=results[1]
    )

    log.warning(msg=f'Did not render bc results are empty!')
    return render_template('services_results.j2', empty=True, threshold=selected_threshold)


@courses_bp.route('/request/orders', methods=['GET'])
@requires_login
@requires_permission
def get_request_orders():
    log.info(msg=f'Renders order selection page')
    return render_template('order_selection.html')


@courses_bp.route('/list/services', methods=['GET'])
@requires_login
@requires_permission
def list_services():
    selected_lang = 'All languages'
    results = courses.GLOBAL_COURSE_CONTROLLER.get_services_for_language(selected_lang)

    if results[0]: return render_template(
        'services_results.j2',
        has_options=True,
        language=selected_lang,
        options=results[1])

    log.warning(msg=f'Did not render bc results are empty!')
    return render_template('services_results.j2', empty=True, language='Any')


@courses_bp.route('/delete/services', methods=['POST'])
@requires_login
@requires_permission
def delete_service():
    log.info(msg=f'Will try to delete service with id {request.form.get("service_id")}')
    courses.GLOBAL_COURSE_CONTROLLER.remove_service(request.form.get('service_id'))
    return redirect(url_for('courses_bp.list_services'))


@courses_bp.route('/add/services', methods=['GET', 'POST'])
@requires_login
@requires_permission
def add_service():
    if request.method == 'POST':
        log.info(msg=f'Request to add new service')
        new_service = { key: value for key, value in request.form.items() if value is not None and str(value) != '' }
        courses.GLOBAL_COURSE_CONTROLLER.add_service(new_service)
        return render_template('services_add.j2', show_redirect=True)

    return render_template('services_add.j2', show_redirect=False)


@courses_bp.route('/cart', methods=['GET', 'POST'])
@requires_login
@requires_permission
def show_cart():
    log.info(msg=f'Renders cart page')
    if request.method == 'GET':
        services = courses.GLOBAL_COURSE_CONTROLLER.fetch_all_services()
        services = services[1] if services[0] else False
        cart = get_cart()
        return render_template('cart.html', items=services, cart=cart)

    log.debug(msg=f'Request to add item in the cart recieved')
    service_to_add = request.values.get('service_id', '')
    add_to_cart(service_to_add)
    return redirect(url_for('courses_bp.show_cart'))
    # render the cart page
    # if post, add/remove item?
    # bruh


@courses_bp.route('/create-order', methods=['POST'])
@requires_login
@requires_permission
def create_order():
    log.info(msg=f'Request to create new order recieved')
    
    # create order record in the database from user data
    cart = get_cart()
    client = session['group_name']
    courses.GLOBAL_COURSE_CONTROLLER.create_new_order(order_details=cart, client=client)

    return redirect(url_for('courses_bp.show_cart'))


@courses_bp.route('/clear-cart', methods=['POST'])
@requires_login
@requires_permission
def clear_cart():
    log.info(msg=f'Request to clear the cart recieved')
    # call delete from cart
    # further can moved into controller logic maybe?
    # if only the cart will be persistent in the database
    delete_from_cart()
    return redirect(url_for('courses_bp.show_cart'))
    
