from register import db

class MENUES(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    menue_name = db.Column(db.String(32), nullable=False)
    value = db.Column(db.Integer())
    short_name = db.Column(db.String(32))
    text = db.Column(db.String(128))
