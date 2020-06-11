import json

from flask import Flask, render_template
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


# endregion a

if __name__ == '__main__':
    app.run()
