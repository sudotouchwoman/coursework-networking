from json import loads, dumps
from json.decoder import JSONDecodeError

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
)

from app import make_logger
from app.policies import requires_login, requires_permission
from controller.patients import PatientController
from controller.hospital import HospitalController

patients_view = make_logger(__name__, 'logs/patients.log')

patients_bp = Blueprint(
    'patients_bp',
    __name__,
    template_folder='templates/',
    static_folder='static/')

@patients_bp.route('menu', methods=['GET'])
@requires_login
@requires_permission
def menu():
    patients_view.info(msg=f'Renders patients menu page')
    return render_template('patient_menu.j2')


@patients_bp.route('/add', methods=['POST', 'GET'])
@requires_login
@requires_permission
def add_new_patient():
    patients_view.info(msg=f'Renders page for new patient record creation')

    if request.method == 'GET':
        return render_template('patient_create.j2')

    attributes = ('first_name', 'passport', 'second_name', 'date_birth', 'city', 'initial_diagnosis')
    new_patient_data = { attribute: request.values.get(attribute) for attribute in attributes }

    status = PatientController().create_patient_record(new_patient_data)
    return render_template('patient_create.j2', status=True, success=status)


@patients_bp.route('/discharge', methods=['POST', 'GET'])
@requires_login
@requires_permission
def list_dischargable():
    patients_view.info(msg=f'Renders page for patient discharging')

    if request.method == 'GET':
        with_diag = PatientController().fetch_dischargable_patients()
        return render_template('patient_discharge.j2', with_diag=with_diag)

    to_remove_id = request.values.get('to_remove_id')
    attending_doc_id = request.values.get('attending_doctor')
    chamber_id = request.values.get('occupied_chamber')

    PatientController().discharge_patient(to_remove_id, attending_doc_id, chamber_id)
    with_diag = PatientController().fetch_dischargable_patients()

    return render_template('patient_discharge.j2', show_alert=True, with_diag=with_diag)


@patients_bp.route('/list', methods=['POST', 'GET'])
@requires_login
@requires_permission
def list_patients():
    patients_view.info(msg=f'Renders patient list')

    patients = PatientController().fetch_unassigned()

    if patients is None:
        patients_view.warning(msg=f'Renders empty page bc fetched data is empty')
        return render_template('hospital_empty.j2')

    if request.method == 'GET':
        
        if 'assign_response' not in request.values:
                return render_template(
                'patient_list.j2',
                patients=patients)

        assign_response = loads(request.values['assign_response'])

        return render_template(
            'patient_list.j2',
            patients=patients,
            has_response=True,
            assign_response=assign_response)

    departments = HospitalController().get_department_list()
    patient = request.values.get('patient_id')
    patient = PatientController().find_patient(patient)

    return render_template(
        'patient_list.j2',
        has_departments=True,
        departments=departments,
        detailed_patient_data=patient,
        patients=patients)


@patients_bp.route('/assign', methods=['POST'])
@requires_login
@requires_permission
def assign_to_department():
    patients_view.info(msg=f'Recieved request to assign patient into department')

    to_assign = request.values.get('patient_id')
    where_to_assign = request.values.get('department_id')

    assign_response = PatientController().assign_patient(to_assign, where_to_assign)
    patients_view.debug(msg=f'Redirects back to patient list')
    return redirect(url_for('.list_patients', assign_response=dumps(assign_response)))


@patients_bp.route('/department', methods=['GET', 'POST'])
@requires_login
@requires_permission
def department_report():
    patients_view.info(msg=f'Renders department report')
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
        patients_view.error(msg=f'Failed to collect request data\
            expected title and id, found: {department_data}')
        return redirect(url_for('page_not_found_redirect'))

    report = HospitalController().make_department_report(d_id, d_title)
    return render_template('hospital_department.j2', departments=departments, report=report)
