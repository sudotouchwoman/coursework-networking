from json import loads
from json.decoder import JSONDecodeError

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    session
)

from app import make_logger
from app.policies import requires_login, requires_permission
from controller.hospital import HospitalController

view_logger = make_logger(__name__, 'logs/hospital.log')

hospital_bp = Blueprint(
    'hospital_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@hospital_bp.route('menu', methods=['GET'])
@requires_login
@requires_permission
def menu():
    view_logger.info(msg=f'Renders hospital menu page')
    return render_template('hospital_menu.j2')


@hospital_bp.route('/assigned-patients', methods=['GET'])
@requires_login
@requires_permission
def assignment_list():
    view_logger.info(msg=f'Renders assignation list for {session["name"]}')
    assigned = HospitalController().get_assigned_to_doctor(session['id'])
    return render_template('hospital_doctor.j2', assigned=assigned)


@hospital_bp.route('/appointments', methods=['GET', 'POST'])
@requires_login
@requires_permission
def list_appointments():
    view_logger.info(msg=f'Renders appointment list')
    if request.method == 'GET':
        doctor_id = session['id']
        appointments = HospitalController().filter_appointments(by='doctor', value=doctor_id)

        if appointments is None: return render_template('appointment_list.j2')

        return render_template(
            'appointment_list.j2',
            appointments=appointments
        )

    if 'action' not in request.values.keys(): return redirect(url_for('page_not_found_redirect'))
    if 'appointment_id' not in request.values.keys(): return redirect(url_for('page_not_found_redirect'))

    HospitalController().update_appointment(request.values['action'], request.values['appointment_id'])
    return redirect(url_for('.list_appointments'))


@hospital_bp.route('/department', methods=['GET', 'POST'])
@requires_login
@requires_permission
def department_report():
    view_logger.info(msg=f'Renders department report')
    departments = HospitalController().get_department_list()
    
    if request.method == 'GET':
        # render as default
        return render_template('hospital_department.j2', departments=departments)

    department_data = request.values.get('selected_department')
    try:
        # try to decode option from the request
        # redirect to 404 handler if something goes wrong
        department_data = loads(department_data)
        d_id = department_data['id']
        d_title = department_data['title']
    
    except (JSONDecodeError, KeyError):
        view_logger.error(msg=f'Failed to collect request data\
            expected title and id, found: {department_data}')
        return redirect(url_for('page_not_found_redirect'))

    report = HospitalController().make_department_report(d_id, d_title)
    return render_template('hospital_department.j2', departments=departments, report=report)

