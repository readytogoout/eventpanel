import peewee
from flask import Blueprint, abort, request, flash, redirect, url_for

from util import templated, auth_required, has_access_to_event


def get_blueprint():
    from database import Event, Instance, EventManagerRelation, EventManager
    blueprint = Blueprint('event', __name__, url_prefix='/event')

    @blueprint.route('/<int:event_id>/admin')
    @auth_required(has_access_to_event('event_id'))
    @templated('event/admin.html')
    def admin(event_id: int):
        e: Event = Event.get_or_none(event_id)
        if e is None:
            abort(404)
        i: Instance = Instance.get(Instance.name == e.instance)
        return dict(name=e.name, event_id=e.event_id, instance=i.name, instance_host=i.hostname)

    @blueprint.route('/<int:event_id>/admin/eventmanager', methods=['POST'])
    @auth_required(has_access_to_event('event_id'))
    def add_event_manager(event_id: int):
        admin_identifier = request.form.get('admin-identifier')
        if admin_identifier is None:
            flash('Missing Email')
            return redirect(url_for(".admin", event_id=event_id))

        eventmanager = EventManager.get_or_none((EventManager.username == admin_identifier)
                                                | (EventManager.email == admin_identifier))

        if eventmanager is None:
            flash('Invalid username or email')
            return redirect(url_for(".admin", event_id=event_id))

        try:
            EventManagerRelation.create(manager_id=eventmanager.username, event_id=event_id)
            flash('Success')

        except peewee.IntegrityError:
            flash('Already satisfied')

        return redirect(url_for(".admin", event_id=event_id))

    return blueprint
