from flask import Blueprint, request, jsonify, g, abort
from models import User
from extensions import db
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from security import data, text, own_user, coordinate, save_photo

user_bp = Blueprint('user', __name__)

def profile(user):
    photo = user.photo_url
    if not photo or photo == 'https://example.com/photo.jpg':
        photo = '/static/avatar.svg'
    return {'id': user.id, 'username': user.username, 'photo_url': photo, 'location': user.location,
            'skills': user.skills or '', 'team_id': user.team_id, 'latitude': user.latitude, 'longitude': user.longitude}

@user_bp.route('/<int:user_id>')
def get_user(user_id):
    return jsonify(profile(db.get_or_404(User, user_id)))

@user_bp.route('/update', methods=['POST'])
def update_user():
    body = data()
    user = own_user(body.get('user_id'))
    username = text(body.get('username', user.username), 'Benutzername', 50, True)
    if User.query.filter(User.username == username, User.id != user.id).first():
        abort(409, description='Dieser Benutzername ist bereits vergeben.')
    user.username = username
    user.location = text(body.get('location', user.location or ''), 'Ort', 100)
    user.skills = text(body.get('skills', user.skills or ''), 'Skills', 300)
    user.latitude = coordinate(body.get('latitude', user.latitude), 90)
    user.longitude = coordinate(body.get('longitude', user.longitude), 180)
    db.session.commit()
    return jsonify(message='Profil aktualisiert.')

@user_bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    user = own_user(request.form.get('user_id'))
    user.photo_url = save_photo(request.files.get('photo'))
    db.session.commit()
    return jsonify(message='Profilbild aktualisiert.', photo_url=user.photo_url)

@user_bp.route('/search')
def search_users():
    skill = request.args.get('skill', '')
    return jsonify([profile(u) for u in User.query.filter(User.skills.ilike(f'%{skill}%')).order_by(User.id)])

@user_bp.route('/location', methods=['POST'])
def update_location():
    body = data()
    user = own_user(body.get('user_id'))
    user.latitude = coordinate(body.get('latitude'), 90)
    user.longitude = coordinate(body.get('longitude'), 180)
    user.last_active = datetime.utcnow()
    db.session.commit()
    return jsonify(message='Standort aktualisiert.')

@user_bp.route('/nearby')
def find_nearby_users():
    own_user(request.args.get('user_id'))
    radius = request.args.get('radius', default=30, type=int)
    if radius is None or not 1 <= radius <= 1000:
        abort(400, description='Bitte einen Radius zwischen 1 und 1000 km angeben.')
    current = g.user
    if current.latitude is None or current.longitude is None:
        abort(400, description='Bitte zuerst deinen Standort im Profil setzen.')
    nearby = []
    for user in User.query.all():
        if user.id == current.id or user.latitude is None or user.longitude is None:
            continue
        lat = radians(user.latitude - current.latitude)
        lng = radians(user.longitude - current.longitude)
        a = sin(lat/2)**2 + cos(radians(current.latitude))*cos(radians(user.latitude))*sin(lng/2)**2
        distance = 6371 * 2 * asin(sqrt(min(1, max(0, a))))
        if distance <= radius:
            nearby.append({'id': user.id, 'username': user.username, 'distance_km': round(distance, 2)})
    return jsonify(sorted(nearby, key=lambda u: u['distance_km']))
