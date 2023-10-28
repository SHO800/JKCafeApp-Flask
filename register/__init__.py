import logging

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# ログをすべて握りつぶす
l = logging.getLogger()
l.addHandler(logging.FileHandler("null"))

app = Flask(__name__)
CORS(app)
app.config.from_object('register.config')
socketio = SocketIO(app, cors_allowed_origins="*")

db = SQLAlchemy(app)

import route
import register.database

register.database.is_exist_db()

import register.controllers.schedule
