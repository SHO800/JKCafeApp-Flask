from register import db


class Menus(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    menu_name = db.Column(db.String(32), nullable=False)
    value = db.Column(db.Integer())
    short_name = db.Column(db.String(32))
    text = db.Column(db.String(128))
    toppings = db.relationship('Toppings', backref='menus')
    coupons = db.relationship('MenuCoupons', backref='menus')


class Toppings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('menus.id'))

    topping_name = db.Column(db.String(32))
    value = db.Column(db.Integer)


class MenuCoupons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent = db.Column(db.Integer, db.ForeignKey('menus.id'))

    coupon_name = db.Column(db.String(32))
    value = db.Column(db.Integer)