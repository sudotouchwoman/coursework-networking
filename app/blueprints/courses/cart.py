from flask import (
    current_app,
    session
)

from app.content.courses.courses import GLOBAL_COURSE_CONTROLLER

# better use database connection for this,
# but still better than storing everything in a single cookie
if 'CARTS' not in current_app.config:
    current_app.config['CARTS'] = {}

def get_cart():
    name = session.get('group_name')
    return current_app.config['CARTS'].get(name, False)

def add_to_cart(item: str):
    name = session.get('group_name')
    if name not in current_app.config['CARTS']: current_app.config['CARTS'][name] = []
    
    service = GLOBAL_COURSE_CONTROLLER.find_service(item)
    if not service[0]: return

    current_app.config['CARTS'][name].append(service[1])


def delete_from_cart():
    name = session.get('group_name')
    if name in current_app.config['CARTS']:
        current_app.config['CARTS'].pop(name)
