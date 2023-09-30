from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object('register.config')
socketio = SocketIO(app)


db = SQLAlchemy(app)

import route
import register.database


register.database.is_exist_db()
