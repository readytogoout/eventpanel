from peewee import *

from app import db


class Instance(db.Model):
    name = CharField(primary_key=True)
    hostname = CharField()


class EventManager(db.Model):
    username = CharField()
    password = CharField()
    email = CharField()


class Event(db.Model):
    name = CharField()
    instance = ForeignKeyField(Instance)


class EventManagerRelation(db.Model):
    manager = ForeignKeyField(EventManager)
    event = ForeignKeyField(Event)


class EventAttendee(db.Model):
    event = ForeignKeyField(Event)


__all_tables__ = ('Instance', 'EventManager', 'Event', 'EventManagerRelation', 'EventAttendee')
__all__ = __all_tables__

# lmao was für ein idiot hat das geschrieben
# ah, ja genau: ich
db.database.create_tables([eval(table) for table in __all_tables__], safe=True)
