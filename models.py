from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Email(db.Model):
    id = db.Column(db.String, primary_key=True)  # Correct usage of db.Column
    text = db.Column(db.Text)
    time = db.Column(db.Integer)
    discarded = db.Column(db.Boolean, default=False)
    labels = db.relationship('Label', backref='email', lazy=True)

class Label(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Correct usage of db.Column
    email_id = db.Column(db.String, db.ForeignKey('email.id'), nullable=False)
    event_name = db.Column(db.String)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
