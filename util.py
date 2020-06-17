import base64
import functools
import hashlib
import random
import string

import bcrypt

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

def pw_gen(pw_len=8, chars=string.ascii_letters + string.digits + string.punctuation):
    return ''.join(random.choice(chars) for _ in range(pw_len))

def pre_encode_password(password: str):
    """
    Still needs encoding using :meth:`bcrypt.hashpw`
    """
    return base64.b64encode(hashlib.sha256(password.encode(encoding='utf-8')).digest())

def register_user(username: str, email: str, plain_password: str, site_admin: bool = False):
    import database as models
    return models.EventManager.create(username=username, email=email,
                                      password=bcrypt.hashpw(pre_encode_password(plain_password), bcrypt.gensalt()),
                                      site_admin=site_admin)