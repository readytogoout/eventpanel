import functools

from flask import session, url_for, redirect, flash, request, render_template


def has_access_to_event(parameter_name: str):
    from database import EventManagerRelation

    def wrapper(*args, **kwargs):
        try:
            next(iter(EventManagerRelation.select(
                EventManagerRelation.event == kwargs.get(parameter_name)
                and (EventManagerRelation.manager == session['username'])
            )))
            return True
        except:
            return False

    return wrapper


def auth_required(*auth_functions, requires_site_admin=False):
    def wrapper(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            is_admin = session.get('admin', False)
            if session.get('username') is None:
                flash('Login using your Event Manager Account first')
            elif requires_site_admin and not is_admin:
                flash('Site Admin Only', 'error')
            elif not is_admin and not all(func(*args, **kwargs) for func in auth_functions):
                flash('Unauthorized Access')
            else:
                return f(*args, **kwargs)

            return redirect(url_for('login_form', redirect_to=request.url))

        return decorated_function

    return wrapper


def templated(template):
    def wrapper(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            return render_template(template, **f(*args, **kwargs))

        return decorated_function

    return wrapper

