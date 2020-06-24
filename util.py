import base64
import functools
import hashlib
import random
import string

import bcrypt
import peewee
import requests
from flask import session, url_for, redirect, flash, request, render_template

from mailing import Mailsender, AttendeeRegistration
from rdyapi import RdyApi


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


def pw_gen(pw_len=8, use_special_chars=True):
    chars = string.ascii_letters + string.digits
    if use_special_chars:
        chars += string.punctuation

    return ''.join(random.choice(chars) for _ in range(pw_len))


def pre_encode_password(password: str):
    """
    Still needs encoding using :meth:`bcrypt.hashpw`
    """
    return base64.b64encode(hashlib.sha256(password.encode(encoding='utf-8')).digest())


def register_eventmanager(username: str, email: str, plain_password: str, site_admin: bool = False):
    import database as models
    return models.EventManager.create(username=username, email=email,
                                      password=bcrypt.hashpw(pre_encode_password(plain_password), bcrypt.gensalt()),
                                      site_admin=site_admin)


def register_event_attendee(instance_hostname, api_key, event_id, username, password, group_id, email="", sendmail=True):
    import database as models
    try:
        api = RdyApi(instance_hostname, api_key)
        api.create_user(group_id=group_id,
                        username=username,
                        password=password)
    except requests.exceptions.ConnectionError:
        flash("Server not reachable!", 'error')
        return

    except:
        flash("Server error!", 'error')
        return
    group: models.Groups = models.Groups.get(group_id=group_id)
    event: models.Event = models.Event.get(event_id=event_id)
    try:
        models.EventAttendee.create(name=username,
                                    event_id=event_id,
                                    group_id=models.Groups.select(models.Groups.id)
                                    .where(models.Groups.group_id == group_id))
    except peewee.IntegrityError:
        flash("This group does not exist in the Database of the admin page!", 'error')

    # TODO create registrationmail for attendees
    if sendmail:
        with Mailsender():
            AttendeeRegistration().send(email, username, password, group.name, event.name, event.instance.hostname)


def register_event_group(instance_hostname, api_key, event_id, groupname, hasSyncedNPCs):
    import database as models
    group_id = pw_gen(pw_len=32, use_special_chars=False)

    try:
        api = RdyApi(instance_hostname, api_key)
        api.create_group(group_id, groupname)

    except requests.exceptions.ConnectionError:
        flash("Server not reachable!", 'error')
        return

    models.Groups.create(name=groupname, group_id=group_id, event_id=event_id, has_synced_npcs=hasSyncedNPCs)
