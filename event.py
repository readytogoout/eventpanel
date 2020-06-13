from flask import Blueprint, abort

from util import templated, auth_required, has_access_to_event


def get_blueprint():
    from database import Event, Instance
    blueprint = Blueprint('event', __name__, url_prefix='/event')

    @blueprint.route('/<int:event_id>/admin')
    @auth_required(has_access_to_event('event_id'))
    @templated('event/admin.html')
    def admin(event_id: int):
        e: Event = Event.get_or_none(event_id)
        i: Instance = Instance.get(Instance.name == e.instance)
        if e is None:
            abort(404)
        return dict(name=e.name, event_id=e.event_id, instance=i.name, instance_host=i.hostname)

    return blueprint
