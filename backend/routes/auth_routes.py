from flask import Blueprint, request, jsonify, g, abort
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Team, RevokedToken
from flask_jwt_extended import create_access_token, get_jwt
from security import data, text, integer, coordinate, save_photo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    form = request.form
    username = text(form.get('username', ''), 'Benutzername', 50, True)
    password = form.get('password', '')
    if not password or len(password) > 200:
        abort(400, description='Bitte ein Passwort angeben (maximal 200 Zeichen).')
    team_id = integer(form.get('team_id'), 'Team') if form.get('team_id') else None
    if team_id is not None:
        db.get_or_404(Team, team_id)
    latitude = coordinate(form.get('latitude'), 90)
    longitude = coordinate(form.get('longitude'), 180)
    if (latitude is None) != (longitude is None):
        abort(400, description='Bitte beide Standortkoordinaten angeben.')
    if User.query.filter_by(username=username).first():
        return jsonify(message='Dieser Benutzername ist bereits vergeben.'), 400
    photo = request.files.get('photo')
    user = User(username=username, password=generate_password_hash(password), team_id=team_id,
                skills=text(form.get('skills', ''), 'Skills', 300),
                location=text(form.get('location', ''), 'Ort', 100),
                latitude=latitude, longitude=longitude,
                photo_url=save_photo(photo) if photo and photo.filename else '/static/avatar.svg')
    db.session.add(user)
    db.session.commit()
    return jsonify(message='Registrierung erfolgreich.'), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    body = data()
    username = text(body.get('username', ''), 'Benutzername', 50, True)
    password = body.get('password')
    if not isinstance(password, str) or not password or len(password) > 200:
        abort(400, description='Bitte ein gültiges Passwort eingeben.')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify(access_token=create_access_token(identity=str(user.id)), user_id=user.id)
    return jsonify(message='Benutzername oder Passwort ist falsch.'), 401

@auth_bp.route('/me')
def me():
    return jsonify(user_id=g.user.id, username=g.user.username, team_id=g.user.team_id)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    db.session.merge(RevokedToken(jti=get_jwt()['jti']))
    db.session.commit()
    return jsonify(message='Abgemeldet.')
