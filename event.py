import json

import peewee
import requests
from flask import Blueprint, abort, request, flash, redirect, url_for, request

from util import templated, auth_required, has_access_to_event, pw_gen, register_event_attendee, register_event_group
from rdyapi import RdyApi


def get_blueprint():
    from database import Event, Instance, EventManagerRelation, EventManager, EventAttendee, Groups, DoesNotExist
    blueprint = Blueprint('event', __name__, url_prefix='/event')

    @blueprint.route('/<int:event_id>/admin')
    @auth_required(has_access_to_event('event_id'))
    @templated('event/admin.html')
    def admin(event_id: int):
        e: Event = Event.get_or_none(event_id)
        if e is None:
            abort(404)

        try:
            i: Instance = Instance.get(Instance.name == e.instance)

            api = RdyApi(i.hostname, i.api_key)
            groups = api.get_groups()

        except json.decoder.JSONDecodeError:
            abort(500, 'API Key invalid!')

        except DoesNotExist:
            abort(500, 'Instance does not Exist!')

        return dict(name=e.name,
                    event_id=e.event_id,
                    instance=i.name,
                    instance_host=i.hostname,
                    groups=groups
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

        if username is None or groupID is None:
            return redirect(url_for('.admin', event_id=event_id))

        instance = list(Instance.select(Instance)
                        .join(Event, on=(Event.instance_id == Instance.name))
                        .where(Event.event_id == event_id)
                        .namedtuples())

        register_event_attendee(instance[0].hostname,
                                instance[0].api_key,
                                event_id,
                                username,
                                pw_gen(8),
                                groupID)

        return redirect(url_for(".admin", event_id=event_id))

    @blueprint.route('/<int:event_id>/admin/eventgroup', methods=['POST'])
    @auth_required(has_access_to_event('event_id'))
    def add_event_group(event_id):
        instance = list(Instance.select(Instance)
                        .join(Event, on=(Event.instance_id == Instance.name))
                        .where(Event.event_id == event_id)
                        .namedtuples())

        groupname = request.form.get('groupname')

        register_event_group(instance[0].hostname, instance[0].api_key, event_id, groupname)

        return redirect(url_for(".admin", event_id=event_id))

    @blueprint.route('/eventinvitation/<string:event_id>', methods=['GET'])
    def eventinvitation(event_id):
        # create group
        return None

    @blueprint.route('/registerattendee/<string:groupId>')
    @templated('invitation system/group.html')
    def registerattendee(groupId):
        if not groupId is None:
            group = Groups.get_or_none((Groups.group_id == groupId))
            if group is None:
                # group-id not in database -> abort
                abort(404)
            else:
                event = Event.get_or_none(Event.event_id == group.event_id)
                if event is None:
                    # event_id in group is not registered
                    abort(500)
                else:
                    instance = Instance.get_or_none(Instance.name == event.instance_id)
                    if instance is None:
                        abort(500)
        else:
            abort(400)
        # PLSS WHY DIDN'T I CHOOSE A JOIN

        registersuccess = request.args.get('registersuccess')
        if registersuccess is None:
            registersuccess = False

        username = request.args.get('username')

        return dict(group=group,
                    event=event,
                    instance=instance,
                    registersuccess=registersuccess,
                    username=username)

    @blueprint.route('/registerattendee/<string:groupId>', methods=['POST'])
    def handleattendeereg(groupId):
        username = request.form.get('username')
        email = request.form.get('email')

        queryresp = list(Groups.select(Instance.hostname, Instance.api_key, Event.event_id)
            .join(Event, on=(Groups.event_id == Event.event_id))
            .join(Instance, on=(Event.instance_id == Instance.name))
            .where(Groups.group_id == groupId)
            .namedtuples())

        register_event_attendee(queryresp[0].hostname, queryresp[0].api_key, queryresp[0].event_id, username, pw_gen(8), groupId, email=email)

        return redirect(url_for('.registerattendee', groupId=groupId, registersuccess=True, username=username))

    return blueprint
