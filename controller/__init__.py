from os import getenv
from abc import ABC
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from schema import *

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/patients.log')
log.disabled = getenv('LOG_ON', "True") == "False"

log.setLevel(getattr(logging, DEBUGLEVEL))
handler = TimedRotatingFileHandler(filename=f'{LOGFILE}', encoding='utf-8', when='h', interval=5, backupCount=0)
formatter = logging.Formatter('[%(asctime)s]::[%(levelname)s]::[%(name)s]::%(message)s', '%D # %H:%M:%S')
handler.setFormatter(formatter)
log.addHandler(handler)

def validate_string(given, expected: str) -> bool:
    try:
        validator = Schema(eval(expected))
        validator.validate(data=given)
        return True
    except SchemaError as scherr:
        log.error(msg=f'Validation error occured: {scherr}')
        return False
    except Exception as e:
        log.fatal(msg=f'Something went wrong during validation, exception info: {e}')
        return False


def validate_object(given, expected) -> bool:
    try:
        validator = Schema(expected)
        validator.validate(data=given)
        return True
    except SchemaError as scherr:
        log.error(msg=f'Validation error occured: {scherr}')
        return False
    except Exception as e:
        log.fatal(msg=f'Something went wrong during validation, exception info: {e}')
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
