from datetime import datetime
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(200))
    location = db.Column(db.String(100))
    skills = db.Column(db.String(300))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    last_active = db.Column(db.DateTime)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    members = db.relationship('User', backref='team', lazy=True)
    ablage = db.Column(db.Text)  # Datenablage/Notizen

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    seen = db.Column(db.Boolean, default=False)
