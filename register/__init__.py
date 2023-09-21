from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO


app = Flask(__name__)
app.config.from_object('register.config')
socketio = SocketIO(app)

db = SQLAlchemy(app)

import route
import register.database


register.database.is_exist_db()