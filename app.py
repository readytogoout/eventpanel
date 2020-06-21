import random
from sqlite3 import sqlite_version as SQLITE_VERSION
from sys import version as PYTHON_VERSION

import bcrypt
import click
import peewee
from flask import Flask, render_template, redirect, request, flash, url_for, session, abort
from flask import __version__ as FLASK_VERSION
from flask_peewee.db import Database

from admin import get_blueprint as get_admin_blueprint
from event import get_blueprint as get_event_blueprint
from mailing import Mailsender, ApplicationSentMail, NewApplicationMail
from util import auth_required, templated, register_eventmanager, pre_encode_password
from version import VERSION as EVENTPANEL_VERSION
from rdyapi import RdyApi

app = Flask(__name__)
app.config.from_json('data/config.json')
app.secret_key = app.config['SECRET_KEY']
db = Database(app)

# noinspection PyUnresolvedReferences
import database as models


@app.context_processor
def global_jinja_injection():
    return dict(
        logged_in='username' in session,
        is_admin=session.get('admin', False),
        username=session.get('user'),
        wins_legit_iphone=random.randint(0, 200) == 42,
    )


# region a
@app.route('/', methods=['GET', 'POST', 'PUT'])
@templated('index.html')
def index():
    if 'username' in session:
        username = session['username']
        event_list = list(models.EventManagerRelation.select(models.Event.name, models.Event.event_id)
                          .join(models.Event, on=models.Event.event_id == models.EventManagerRelation.event_id)
                          .where(models.EventManagerRelation.manager == username)
                          .namedtuples()
                          )
        print(event_list)
        return dict(events=event_list)
    else:
        return dict()


@app.route('/info')
@templated('info.html')
def info():
    return dict(
        versions=dict(
            eventpanel=EVENTPANEL_VERSION,
            python=PYTHON_VERSION,
            flask=FLASK_VERSION,
            sqlite_driver=SQLITE_VERSION,
            sqlite='.'.join(map(str, models.db.database.server_version)),
        )
    )


@app.route('/<int:u>')
@auth_required()
def goodbye(u: int):
    print(u)
    flash(f'{u + 3}', category='error')
    return render_template('number.html', number=u)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None:
        flash("Please enter a username", category="error")
        return redirect(url_for('login_form'))
    if password is None:
        flash("Please enter a password", category="error")
        return redirect(url_for('login_form'))
    redirect_url = request.form.get('redirect', '/')
    e: models.EventManger = models.EventManager.get_or_none(username=username)
    if e is None:
        flash("Unknown username", category="error")
        return redirect(url_for('login_form'))
    if bcrypt.checkpw(pre_encode_password(password), e.password.encode('utf-8')):
        session['username'] = username
        session['admin'] = e.site_admin
        return redirect(redirect_url, code=302)
    else:
        flash("Invalid password", category="error")
        return redirect(url_for('login_form'))


@app.route('/apply', methods=['POST'])
def apply():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    persons = request.form.get('persons')
    message = request.form.get('message', '')
    if not all([first_name, last_name, email, persons]):
        return redirect('https://readytogoout.games/#invalidapplication')

    application = models.Application.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        count=persons,
        message=message,
    )
    with Mailsender():
        ApplicationSentMail().send(email)
        NewApplicationMail().send('kontakt@readytogoout.games', application)
    return redirect('https://readytogoout.games/mailsuccess/')


@app.route('/apply', methods=['GET'])
def apply_redirect():
    return redirect('https://readytogoout.games/')


@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

# endregion a
app.register_blueprint(get_event_blueprint())
app.register_blueprint(get_admin_blueprint())


@app.route('/logout', methods=['GET'])
@auth_required()
@templated('logout.html')
def logout():
    session.clear()
    return dict()


@app.cli.command('clear-db', help='Obliterate the database file')
def clear_db_command():
    import os
    d: peewee.SqliteDatabase = db.database
    d.close()
    os.unlink('data/data.db')


@app.cli.command('add-admin', help='Adds an admin or event manager to the db')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@click.option('--admin', is_flag=True, help='Make them a site admin')
def add_admin_command(username, email, password, admin):
    u = register_eventmanager(username, email, password, admin)
    print(f'User {u.username} created.')


if __name__ == '__main__':
    app.run()
