# project/models.py


import datetime

from project import db, bcrypt


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    events = db.relationship('Event', backref='author', lazy='dynamic')

    scores = db.relationship('Score', backref='author', lazy='dynamic')

    def __init__(self, email, password, paid=False, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<email {}'.format(self.email)

class Event(db.Model):

    # __tablename__ = "Event"

    id = db.Column(db.Integer,unique=True,primary_key=True)
    desc = db.Column(db.String(80),nullable=False) #,unique=True) #,primary_key=True)
    want = db.Column(db.String,nullable=False)
    likelihood = db.Column(db.Integer,nullable=False)
    happened = db.Column(db.String,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # def __init__(self, desc, want, likelihood, happened):
    #     self.desc = desc
    #     self.want = want
    #     self.likelihood = likelihood
    #     self.happened = happened

class Score (db.Model):

    id = db.Column(db.Integer,unique=True,primary_key=True)
    scored_on = db.Column(db.DateTime, nullable=False)
    reality = db.Column(db.Integer,nullable=False)
    accuracy = db.Column(db.Integer,nullable=False)
    num = db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
