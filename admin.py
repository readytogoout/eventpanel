from flask import Flask, Blueprint, render_template
from flask_peewee.db import Database


def get_blueprint(app: Flask, db: Database) -> Blueprint:
    blueprint = Blueprint('admin', __name__, url_prefix='/admin')

    @blueprint.route('/')
    def index():
        return render_template('admin.html')

    return blueprint
