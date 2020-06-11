from flask import Flask, render_template, redirect, request
from flask_peewee.db import Database
import bcrypt

app = Flask(__name__)
app.config.from_json('data/config.json')

db = Database(app)

# noinspection PyUnresolvedReferences
import database as models


# region a
@app.route('/', methods=['GET', 'POST', 'PUT'])
def hello_world():
    return 'Hello World!'


@app.route('/<int:u>')
def goodbye(u: int):
    print(u)
    return render_template('number.html', number=u)


# TODO: sessioncookie
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username is None:
        return "No Username"
    if password is None:
        return "No Password"
    redirect_url = request.form.get('redirect', '/')
    e: models.EventManger = models.EventManager.get_or_none(username=username)
    if e is None:
        return 'Unknown Username'
    if bcrypt.checkpw(password, e.password):
        return redirect(redirect_url, code=302)
    else:
        return "Invalid Username"


@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')


# endregion a

if __name__ == '__main__':
    app.run()
