from peewee import *

from app import db


class EnumField(CharField):
    def __init__(self, enum_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class
        self.max_length = 255

    def db_value(self, value):
        return value.name

    def python_value(self, value):
        return self.enum_class(value)


class Instance(db.Model):
    name = CharField(primary_key=True)
    api_key = CharField()
    hostname = CharField()


class Event(db.Model):
    name = CharField()
    event_id = IntegerField(primary_key=True)
    registration_link = CharField(unique=True, null=True)
    instance = ForeignKeyField(Instance, backref='events')


class Application(db.Model):
    application_id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField()
    email = CharField()
    count = CharField()
    message = CharField(max_length=10000)


class EventManager(db.Model):
    username = CharField(primary_key=True)
    password = CharField()
    site_admin = BooleanField(default=False)
    email = CharField()


class EventManagerRelation(db.Model):
    class Meta:
        primary_key = CompositeKey('manager', 'event')

    manager = ForeignKeyField(EventManager)
    event = ForeignKeyField(Event)


class EventAttendee(db.Model):
    event = ForeignKeyField(Event)


__all__ = ('Instance', 'EventManager', 'Event', 'EventManagerRelation', 'EventAttendee', 'Application')

# lmao was für ein idiot hat das geschrieben
# ah, ja genau: ich
db.database.create_tables([
    Instance, EventManager, Event, EventManagerRelation, EventAttendee, Application
], safe=True)
