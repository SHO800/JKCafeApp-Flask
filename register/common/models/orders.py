from register import db


class Order(db.Model):
    uuid = db.Column(db.String(), nullable=False, primary_key=True)

    checked_out_at = db.Column(db.DateTime, nullable=False)
    total_value = db.Column(db.Integer())
    item = db.relationship('OrderItem', backref='order')
    provided = db.Column(db.Integer())


class OrderItem(db.Model):
    uuid = db.Column(db.String(), primary_key=True)
    parent = db.Column(db.String(), db.ForeignKey(Order.uuid))

    menu_id = db.Column(db.Integer)
    menu_name = db.Column(db.String(32))
    short_name = db.Column(db.String(32))
    value = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    coupon = db.relationship('OrderCoupons', backref='orderItem')
    option = db.relationship('Options', backref='orderItem')
    sum = db.Column(db.Integer)


class Options(db.Model):
    uuid = db.Column(db.String(), primary_key=True)
    parent = db.Column(db.String(), db.ForeignKey(OrderItem.uuid))

    option_name = db.Column(db.String(32))
    value = db.Column(db.Integer)
    quantity = db.Column(db.Integer)


class OrderCoupons(db.Model):
    __table_args__ = {'extend_existing': True}
    uuid = db.Column(db.String(), primary_key=True)
    parent = db.Column(db.String(), db.ForeignKey(OrderItem.uuid))

    coupon_name = db.Column(db.String(32))
    value = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
