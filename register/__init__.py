from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('register.config')

db = SQLAlchemy(app)

import route
import register.database


register.database.is_exist_db()