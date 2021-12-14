from abc import ABC
import datetime

from schema import *

from app import make_logger

def validate_string(given, expected: str) -> bool:
    controller = make_logger(__name__, 'logs/app.log')
    try:
        validator = Schema(eval(expected))
        validator.validate(data=given)
        return True
    except SchemaError as scherr:
        controller.error(msg=f'Validation error occured: {scherr}')
        return False
    except Exception as e:
        controller.fatal(msg=f'Something went wrong during validation, exception info: {e}')
        return False


def validate_object(given, expected) -> bool:
    controller = make_logger(__name__, 'logs/app.log')
    try:
        validator = Schema(expected)
        validator.validate(data=given)
        return True
    except SchemaError as scherr:
        controller.error(msg=f'Validation error occured: {scherr}')
        return False
    except Exception as e:
        controller.fatal(msg=f'Something went wrong during validation, exception info: {e}')
        return False


class Validator(ABC):

    PATIENT_INSERT_TEMPLATE = {
        'first_name': And(str, lambda s: s.isalpha()),
        'second_name': And(str, lambda s: s.isalpha()),
        'passport': And(str, lambda s: not s or s.isdigit()),
        'city': str,
        'date_birth': And(str, lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date() < datetime.date.today()),
        'initial_diagnosis': Or(str, None)
        }

    APPOINTMENT_INSERT_TEMPLATE = {
        'asignee': And(str, lambda s: s.isalpha()),
        'patient': And(str, lambda s: s.isalpha()),
        Optional('about'): str,
        Optional('scheduled'): And(str, lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date() >= datetime.date.today())
    }

    APPOINTMENT_UPDATE_TEMPLATE = {
        'is_final': bool,
        'about': str,
        'schedule_to': Or(And(datetime.datetime, lambda s: s.date() >= datetime.date.today()), None),
        'appointment_id': int,
        'patient_id': int
    }

    DIAGNOSIS_METADATA_TEMPLATE = {
        'patient_id': And(str, lambda s: s.isdigit()),
        'appointment_id': And(str, lambda s: s.isdigit())
    }

    @staticmethod
    def validate_patient_data(patient_data) -> bool:
        return validate_object(patient_data, Validator.PATIENT_INSERT_TEMPLATE)


    @staticmethod
    def validate_appointment_data(appointment_data) -> bool:
        return validate_object(appointment_data, Validator.APPOINTMENT_INSERT_TEMPLATE)


    @staticmethod
    def validate_appointment_schedule(appointment_schedule) -> bool:
        return validate_object(appointment_schedule, Validator.APPOINTMENT_UPDATE_TEMPLATE)


    @staticmethod
    def validate_query_params(params: dict, expected_params: tuple) -> bool:
        template = { param: object for param in expected_params}
        template.update({ str: object })
        return validate_object(params, template)

    
    @staticmethod
    def validate_diagnosis_metadata(request_values) -> bool:
        return validate_object(request_values, Validator.DIAGNOSIS_METADATA_TEMPLATE)
