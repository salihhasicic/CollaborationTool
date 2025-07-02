from flask import Blueprint, request, jsonify
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
from flask_jwt_extended import create_access_token
import uuid
import os
import imghdr

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    
    username = request.form.get('username')
    password = request.form.get('password')
    team_id = request.form.get('team_id')
    skills = request.form.get('skills', '')
    location = request.form.get('location', '')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    
    photo_file = request.files.get('photo')
    photo_url = None

    if photo_file and photo_file.filename != '':
        # Lies einige Bytes, um den Typ zu ermitteln
        header = photo_file.read(512)
        photo_file.seek(0)  # danach wieder zurücksetzen für .save()

        filetype = imghdr.what(None, header)
        if not filetype:
            return jsonify({'message': 'Ungültiger Bildtyp'}), 400  # oder skip speichern

        filename = f"{uuid.uuid4().hex}.{filetype}"  # z.B. 123abc456def.png

        upload_folder = os.path.join(current_app.root_path, '..', 'static', 'photos')
        upload_folder = os.path.abspath(upload_folder)  # normiert den Pfad
        os.makedirs(upload_folder, exist_ok=True)

        save_path = os.path.join(upload_folder, filename)
        photo_file.save(save_path)

        photo_url = f"/static/photos/{filename}"

    hashed_pw = generate_password_hash(password)
    new_user = User(
        username=username,
        password=hashed_pw,
        team_id=team_id,
        skills=skills,
        location=location,
        latitude=latitude,
        longitude=longitude,
        photo_url=photo_url
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': access_token, 'user_id': user.id})
    return jsonify({'message': 'Invalid credentials'}), 401
