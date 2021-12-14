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
        'city': And(str, lambda s: s.isalpha()),
        'date_birth': And(str, lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date() < datetime.date.today()),
        'initial_diagnosis': Or(str, None)
        }

    APPOINTMENT_INSERT_TEMPLATE = {
        'asignee': And(str, lambda s: s.isalpha()),
        'patient': And(str, lambda s: s.isalpha()),
        Optional('about'): str,
        Optional('scheduled'): And(str, lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date() >= datetime.date.today())
    }

    @staticmethod
    def validate_patient_data(patient_data) -> bool:
        return validate_object(patient_data, Validator.PATIENT_INSERT_TEMPLATE)


    @staticmethod
    def validate_appointment_data(appointment_data) -> bool:
        return validate_object(appointment_data, Validator.APPOINTMENT_INSERT_TEMPLATE)
