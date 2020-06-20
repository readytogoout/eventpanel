import peewee
import requests
from flask import Blueprint, abort, request, flash, redirect, url_for, request

from util import templated, auth_required, has_access_to_event, pw_gen
from rdyapi import RdyApi


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
        api = RdyApi(i.hostname, i.api_key)
        return dict(name=e.name,
                    event_id=e.event_id,
                    instance=i.name,
                    instance_host=i.hostname,
                    groups=api.get_groups()
                    )

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

    @blueprint.route('/<int:event_id>/admin/eventattendee', methods=['POST'])
    @auth_required(has_access_to_event('event_id'))
    def add_event_attendee(event_id):
        username = request.form.get('username')
        groupID = request.form.get('group-id')

        instance = list(Instance.select(Instance)
                        .join(Event, on=(Event.instance_id == Instance.name))
                        .where(Event.event_id == event_id)
                        .namedtuples())

        try:
            api = RdyApi(instance[0].hostname, instance[0].api_key)
            api.create_user(group_id=groupID,
                            username=username,
                            password=pw_gen(8))

        except requests.exceptions.ConnectionError:
            flash("Server not reachable!", 'error')
        except Exception as e:
            flash("Server error!", 'error')

        return redirect(url_for(".admin", event_id=event_id))

    @blueprint.route('/<int:event_id>/admin/eventgroup', methods=['POST'])
    @auth_required(has_access_to_event('event_id'))
    def add_event_group(event_id):
        instance = list(Instance.select(Instance)
                    .join(Event, on=(Event.instance_id == Instance.name))
                    .where(Event.event_id == event_id)
                    .namedtuples())

        try:
            api = RdyApi(instance[0].hostname, instance[0].api_key)
            api.create_group(group_id=pw_gen(pw_len=128, use_special_chars=False), # actually a group ID xD
                                   group_name=request.form.get('groupname'))
        except requests.exceptions.ConnectionError:
            flash("Server not reachable!", 'error')
        except Exception as e:
            flash("Server error!", 'error')

        return redirect(url_for(".admin", event_id=event_id))

    return blueprint



