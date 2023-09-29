from register import db


class Order(db.Model):
    checkouted_at = db.Column(db.DateTime, nullable=False, primary_key=True)
    total_value = db.Column(db.Integer())
    item = db.relationship('OrderItem', backref='order')
    provided = db.Column(db.Integer())


class OrderItem(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    parent = db.Column(db.DateTime, db.ForeignKey('order.checkouted_at'))

    menue_name = db.Column(db.String(32))
    short_name = db.Column(db.String(32))
    quantity = db.Column(db.Integer)
    sum_value = db.Column(db.Integer)