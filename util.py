import functools

from flask import session, url_for, redirect, flash, request


def auth_required(requires_site_admin=False):
    def wrapper(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('username') is None:
                flash('Login using your Event Manager Account first')
            elif requires_site_admin and not session.get('admin', False):
                flash('Site Admin Only', 'error')
            else:
                return f(*args, **kwargs)

            return redirect(url_for('login_form', redirect_to=request.url))

        return decorated_function

    return wrapper
