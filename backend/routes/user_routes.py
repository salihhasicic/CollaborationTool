from flask import Blueprint, request, jsonify
from models import User
from extensions import db
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint('user', __name__)

# 🔎 Benutzerprofil anzeigen
@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'photo_url': user.photo_url,
        'location': user.location,
        'skills': user.skills,
        'team_id': user.team_id,
        'latitude': user.latitude,
        'longitude': user.longitude
    })
# 🔎 Benutzerprofil anpassen
@user_bp.route('/update', methods=['POST'])
def update_user():
    data = request.get_json()
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.username = data.get('username', user.username)
    user.location = data.get('location', user.location)
    user.skills = data.get('skills', user.skills)
    user.latitude = data.get('latitude', user.latitude)
    user.longitude = data.get('longitude', user.longitude)

    db.session.commit()
    return jsonify({'message': 'User updated'})

# 🔎 Bild anpassen
@user_bp.route('/upload_photo', methods=['POST'])
def upload_photo():
    from flask import current_app
    import os
    import uuid
    from werkzeug.utils import secure_filename

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404

    photo_file = request.files.get('photo')
    if not photo_file or photo_file.filename == '':
        return jsonify({'message': 'Kein Bild übergeben'}), 400

    # Dateiendung extrahieren
    ext = os.path.splitext(secure_filename(photo_file.filename))[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"

    # Zielordner in /static/photos im Projektverzeichnis
    upload_folder = os.path.abspath(os.path.join(current_app.root_path, '..', 'static', 'photos'))
    os.makedirs(upload_folder, exist_ok=True)

    save_path = os.path.join(upload_folder, unique_filename)
    photo_file.save(save_path)

    # Datenbank aktualisieren
    user.photo_url = f'/static/photos/{unique_filename}'
    db.session.commit()

    return jsonify({'message': 'Profilbild aktualisiert', 'photo_url': user.photo_url})



# 🔍 Suche nach Skill
@user_bp.route('/search', methods=['GET'])
def search_users():
    skill = request.args.get('skill')
    users = User.query.filter(User.skills.like(f"%{skill}%")).all()
    result = [{'id': u.id, 'username': u.username, 'skills': u.skills} for u in users]
    return jsonify(result)

# 📍 Standort speichern
@user_bp.route('/location', methods=['POST'])
def update_location():
    data = request.json
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user.latitude = data['latitude']
    user.longitude = data['longitude']
    user.last_active = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Location updated'})

# 📍 Nutzer im Umkreis finden
@user_bp.route('/nearby', methods=['GET'])
@jwt_required()
def find_nearby_users():
    user_id = request.args.get('user_id', type=int) or int(get_jwt_identity())
    radius_km = request.args.get('radius', default=30, type=int)

    current_user = User.query.get(user_id)
    if not current_user or not current_user.latitude or not current_user.longitude:
        return jsonify({'message': 'Location not set for user'}), 400

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    all_users = User.query.all()
    nearby = []
    for user in all_users:
        if user.id == user_id or not user.latitude or not user.longitude:
            continue
        distance = haversine(current_user.latitude, current_user.longitude, user.latitude, user.longitude)
        if distance <= radius_km:
            nearby.append({
                'id': user.id,
                'username': user.username,
                'distance_km': round(distance, 2)
            })

    return jsonify(nearby)
