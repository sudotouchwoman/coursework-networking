from functools import wraps

from flask import (
    session,
    current_app,
    request,
    render_template)

def authenticated() -> bool:
    group_name = session.get('group_name', '')
    return True if group_name else False


def requires_login(func):

    @wraps(func)
    def has_group(*args, **kwargs):
        return func(*args, **kwargs) if authenticated() else render_template('login.j2')
    
    return has_group


def authorized() -> bool:
    policies = current_app.config['POLICIES']
    group_name = session.get('group_name', 'unauthorized')

    target_service = "" if len(request.endpoint.split('.')) == 1 else request.endpoint.split('.')[0]

    return True if group_name in policies and target_service in policies[group_name] else False


def requires_permission(func):

    @wraps(func)
    def has_permission(*args, **kwargs):
        return func(*args, **kwargs) if authorized() else render_template('permission.j2')
    
    return has_permission
