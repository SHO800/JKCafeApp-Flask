import datetime
import pytz
from register import db


class CHECKOUTS_CHILD(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    parent = db.Column(db.DateTime)

    menue_name = db.Column(db.String(32))
    quantity = db.Column(db.Integer())
    sum_value = db.Column(db.Integer)