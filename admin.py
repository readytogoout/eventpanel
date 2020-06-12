from collections import defaultdict

from flask import Flask, Blueprint, abort
from flask_peewee.db import Database

from util import auth_required, templated


def get_blueprint(app: Flask, db: Database) -> Blueprint:
    from database import Instance, EventManagerRelation, Event
    blueprint = Blueprint('admin', __name__, url_prefix='/admin')

    @blueprint.route('/')
    @auth_required(requires_site_admin=True)
    @templated('admin.html')
    def index():
        instance_list = list(Instance.select(Instance.hostname, Instance.name).namedtuples())
        return dict(instances=instance_list)

    @blueprint.route('/instance/<instance_id>')
    @auth_required(requires_site_admin=True)
    @templated('instance.html')
    def instance_details(instance_id):
        managers = defaultdict(list)
        i = Instance.get_or_none(Instance.name == instance_id)
        if i is None:
            return abort(404)  # todo 404 handler
        event_list = list(Event.select(Event, EventManagerRelation.manager)
                          .join(EventManagerRelation, on=EventManagerRelation.event == Event.event_id)
                          .where(Event.instance == instance_id)
                          .group_by(Event.event_id)
                          .namedtuples())
        for ev in event_list:
            managers[ev.event_id].append(ev.manager)
        return dict(
            events=event_list,
            managers=managers,
            name=instance_id,
            hostname=i.hostname
        )

    return blueprint
