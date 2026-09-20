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
    owner_id = db.Column(db.Integer, nullable=True)
    members = db.relationship('User', backref='team', lazy=True)
    ablage = db.Column(db.Text)  # Datenablage/Notizen

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    seen = db.Column(db.Boolean, default=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="To Do")  # To Do, In Progress, Done
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    tasks = db.relationship('Task', backref='project', lazy=True)
    deadline = db.Column(db.DateTime, nullable=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="To Do")  # To Do, In Progress, Done
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=True)

class PrivateMessage(db.Model):
    __tablename__ = 'private_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class RevokedToken(db.Model):
    jti = db.Column(db.String(64), primary_key=True)

class SchemaMigration(db.Model):
    key = db.Column(db.String(100), primary_key=True)

class TeamFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    storage_name = db.Column(db.String(300), nullable=False)
    uploader = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
