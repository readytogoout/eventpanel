import json

from flask import Flask, render_template
from flask_peewee.db import Database

app = Flask(__name__)
with open('data/config.json') as fp:
    app.config.from_object(json.load(fp))

db = Database(app)


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
