import json

from flask import Flask, render_template, redirect, request
from flask_peewee.db import Database

app = Flask(__name__)
app.config.from_json('data/config.json')

db = Database(app)
from database import *



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
def POST_login():
    username = request.form.get('username')
    password = request.form.get('password')
    redirect_url = request.form.get('redirect')
    if username == "total" and password == "sicher":
        return redirect(redirect_url, code=302)
    else:
        return "Invalid Username"

@app.route('/login', methods=['GET'])
def GET_login():
    return """Hallo Welt"""

# endregion a

if __name__ == '__main__':
    app.run()
