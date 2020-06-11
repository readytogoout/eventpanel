from peewee import *

from app import db


class Instance(db.Model):
    name = CharField(primary_key=True)
    hostname = CharField()


class EventManager(db.Model):
    username = CharField(primary_key=True)
    password = CharField()
    site_admin = BooleanField(default=False)
    email = CharField()


class Event(db.Model):
    name = CharField()
    instance = ForeignKeyField(Instance)


class EventManagerRelation(db.Model):
    manager = ForeignKeyField(EventManager)
    event = ForeignKeyField(Event)


class EventAttendee(db.Model):
    event = ForeignKeyField(Event)


__all__ = ('Instance', 'EventManager', 'Event', 'EventManagerRelation', 'EventAttendee')

# lmao was für ein idiot hat das geschrieben
# ah, ja genau: ich
db.database.create_tables([
    Instance, EventManager, Event, EventManagerRelation, EventAttendee
], safe=True)
