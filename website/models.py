from . import db

class PassRecord(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    url=db.Column(db.String(500))
    login=db.Column(db.String(100))
    remark=db.Column(db.String(500))
    password=db.Column(db.LargeBinary(500))