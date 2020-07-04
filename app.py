import base64
import hashlib

import bcrypt
import click
import peewee
from flask import Flask, render_template, redirect, request, flash, url_for, session
from flask_peewee.db import Database

from admin import get_blueprint as get_admin_blueprint
from event import get_blueprint as get_event_blueprint
from util import auth_required, templated

app = Flask(__name__)
app.config.from_json('data/config.json')
app.secret_key = app.config['SECRET_KEY']
db = Database(app)

# noinspection PyUnresolvedReferences
import database as models


@app.context_processor
def global_jinja_injection():
    return dict(
        logged_in='user' in session,
        is_admin=session.get('admin', False),
        username=session.get('user'),
    )


# region a
@app.route('/', methods=['GET', 'POST', 'PUT'])
@templated('index.html')
def index():
    return dict()


@app.route('/<int:u>')
@auth_required()
def goodbye(u: int):
    print(u)
    flash(f'{u + 3}', category='error')
    return render_template('number.html', number=u)


def pre_encode_password(password: str):
    """
    Still needs encoding using :meth:`bcrypt.hashpw`
    """
    return base64.b64encode(hashlib.sha256(password.encode(encoding='utf-8')).digest())


def register_user(username: str, email: str, plain_password: str, site_admin: bool = False):
    return models.EventManager.create(username=username, email=email,
                                      password=bcrypt.hashpw(pre_encode_password(plain_password), bcrypt.gensalt()),
                                      site_admin=site_admin)


# TODO: sessioncookie
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None:
        flash("Bitte gibt einen Nutzernamen ein", category="error")
        return redirect(url_for('login_form'))
    if password is None:
        flash("Bitte gib ein Passwort ein", category="error")
        return redirect(url_for('login_form'))
    redirect_url = request.form.get('redirect', '/')
    e: models.EventManger = models.EventManager.get_or_none(username=username)
    if e is None:
        flash("Nutzername oder Passwort falsch", category="error")
        return redirect(url_for('login_form'))
    if bcrypt.checkpw(pre_encode_password(password), e.password.encode('utf-8')):
        session['username'] = username
        session['admin'] = e.site_admin
        return redirect(redirect_url, code=302)
    else:
        flash("Nutzername oder Passwort falsch", category="error")
        return redirect(url_for('login_form'))


@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')


# endregion a
app.register_blueprint(get_event_blueprint())
app.register_blueprint(get_admin_blueprint())


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
    u = register_user(username, email, password, admin)
    print(f'User {u.username} created.')


if __name__ == '__main__':
    app.run()
