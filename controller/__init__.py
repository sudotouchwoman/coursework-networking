from os import getenv
import logging
from logging.handlers import TimedRotatingFileHandler

from schema import *

log = logging.getLogger(__name__)
# enable logging routines
# write log to a file with specified filename (provided via environmental variable)
# set needed level and optionally disable logging completely

DEBUGLEVEL = getenv('DEBUG_LEVEL','DEBUG')
LOGFILE = getenv('APP_LOGFILE_NAME', 'logs/log-patients-app-state.log')
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
    except SchemaError as scherr:
        log.error(msg=f'Validation error occured: {scherr}')
        return False
    except Exception as e:
        log.fatal(msg=f'Something went wrong during validation, exception info: {e}')
        return False
    return True


def validate_object(given, expected) -> bool:
    try:
        validator = Schema(expected)
        validator.validate(data=given)
    except SchemaError as scherr:
        log.error(msg=f'Validation error occured: {scherr}')
        return False
    except Exception as e:
        log.fatal(msg=f'Something went wrong during validation, exception info: {e}')
        return False
    return True