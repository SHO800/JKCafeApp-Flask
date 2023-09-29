from register import db

class SESSION_MENUES(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    menue_name = db.Column(db.String(32), nullable=False)
    menue_id = db.Column(db.Integer(), nullable=False)
    short_name = db.Column(db.String(32))
    quantity = db.Column(db.Integer())
    value = db.Column(db.Integer())
    sum_value = db.Column(db.Integer())
