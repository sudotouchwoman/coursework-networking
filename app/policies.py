from functools import wraps

from flask import (
    session,
    current_app,
    request,
    redirect,
    url_for)

def authenticated() -> bool:
    group = session.get('group', '')
    return True if group else False


def requires_login(func):

    @wraps(func)
    def has_group(*args, **kwargs):
        return func(*args, **kwargs) if authenticated() else redirect(url_for('auth_bp.login'))
    
    return has_group


def authorized() -> bool:
    policies = current_app.config['POLICIES']
    group = session.get('group', 'unauthorized')

    target_service = "" if len(request.endpoint.split('.')) == 1 else request.endpoint.split('.')[0]

    return True if group in policies and target_service in policies[group] else False


def requires_permission(func):

    @wraps(func)
    def has_permission(*args, **kwargs):
        return func(*args, **kwargs) if authorized() else redirect(url_for('auth_bp.permission'))
    
    return has_permission
