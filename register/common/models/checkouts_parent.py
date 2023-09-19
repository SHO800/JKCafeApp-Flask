from register import db


class CHECKOUTS_PARENT(db.Model):
    checkouted_at = db.Column(db.DateTime, nullable=False, primary_key=True)
    # id = db.Column(db.Integer, )

    total_value = db.Column(db.Integer())