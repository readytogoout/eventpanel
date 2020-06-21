from collections import defaultdict

import peewee
from flask import Blueprint, abort, request, flash, redirect, url_for
from peewee import JOIN

from mailing import Mailsender, RegistrationMail
from util import auth_required, templated, register_user


def get_blueprint() -> Blueprint:
    from database import Instance, EventManagerRelation, Event, EventManager
    blueprint = Blueprint('admin', __name__, url_prefix='/admin')

    @blueprint.route('/')
    @auth_required(requires_site_admin=True)
    @templated('admin.html')
    def index():
        instance_list = list(Instance.select(Instance.hostname, Instance.name).namedtuples())
        manager_list = list(EventManager.select(
            EventManager.username, EventManager.email, EventManager.site_admin).namedtuples())
        return dict(instances=instance_list, managers=manager_list)

    @blueprint.route('/event/', methods=['POST'])
    @auth_required(requires_site_admin=True)
    def register_event():
        event_name = request.form.get('name')
        instance_id = request.form.get('instance')
        e = Event.create(name=event_name, instance=instance_id)
        return redirect(url_for('event.admin', event_id=e.event_id))

    @blueprint.route('/application/<application_id>')
    @auth_required(requires_site_admin=True)
    def application(application_id: str):
        return str(application_id)

    @blueprint.route('/event-manager/', methods=['POST'])
    @auth_required(requires_site_admin=True)
    def create_user():
        username = request.form.get('username')
        email = request.form.get('email')
        is_site_admin = bool(request.form.get('is-admin', False))
        password = "passwort"  # TODO pw_gen(8)

        if username is None or email is None or is_site_admin is None:
            flash('Please check you\'re input')
            return redirect(url_for('admin.index'))

        try:
            register_user(username, email, password)
            flash('Success')
        except peewee.IntegrityError:
            flash('Username is already taken!')
        with Mailsender() as sender:
            RegistrationMail(sender).send(email, username, password)

        return redirect(url_for('admin.index'))

    @blueprint.route('/instance/', methods=['POST'])
    @auth_required(requires_site_admin=True)
    def register_instance():
        instance_name = request.form.get('name')
        if not instance_name:
            flash('Missing Name')
            return redirect(url_for('.index'))

        api_key = request.form.get('api_key')
        if not api_key:
            flash("No API KEY")
            return redirect(url_for('.index'))

        hostname = request.form.get('hostname')
        if not hostname:
            flash('Missing hostname')
            return redirect(url_for('.index'))

        i, created = Instance.get_or_create(name=instance_name, hostname=hostname,
                                            api_key=api_key)
        if not created:
            flash('This instance name is already in use.')
            return redirect(url_for('.index'))
        return redirect(url_for('.instance_details', instance_id=instance_name))

    @blueprint.route('/instance/<instance_id>')
    @auth_required(requires_site_admin=True)
    @templated('instance.html')
    def instance_details(instance_id):
        managers = defaultdict(list)
        i = Instance.get_or_none(Instance.name == instance_id)
        if i is None:
            return abort(404)  # todo 404 handler
        event_list = list(Event.select(Event, EventManagerRelation.manager)
                          .join(EventManagerRelation, on=EventManagerRelation.event == Event.event_id,
                                join_type=JOIN.LEFT_OUTER)
                          .where(Event.instance == instance_id)
                          .group_by(Event.event_id)
                          .namedtuples())
        for ev in event_list:
            managers[ev.event_id].append(ev.manager)
        return dict(
            events=event_list,
            managers=managers,
            name=instance_id,
            hostname=i.hostname,
            api_key=i.api_key
        )

    return blueprint
