from flask import Flask, Blueprint
from flask_peewee.db import Database

from util import auth_required, templated


def get_blueprint(app: Flask, db: Database) -> Blueprint:
    from database import Instance
    blueprint = Blueprint('admin', __name__, url_prefix='/admin')

    @blueprint.route('/')
    @auth_required(requires_site_admin=True)
    @templated('admin.html')
    def index():
        instance_list = list(Instance.select(Instance.hostname, Instance.name).namedtuples())
        return dict(instances=instance_list)

    return blueprint
