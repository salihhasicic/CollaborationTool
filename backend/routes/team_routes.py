from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import Team, User
from extensions import db
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

team_bp = Blueprint('team', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

def get_files_metadata_path(team_id):
    return os.path.join(UPLOAD_FOLDER, f"team_{team_id}_files.json")

def load_files_metadata(team_id):
    path = get_files_metadata_path(team_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_files_metadata(team_id, files):
    path = get_files_metadata_path(team_id)
    with open(path, "w") as f:
        json.dump(files, f)

# Ändere die Route von '/team' zu einfach nur '/'!
@team_bp.route('/create', methods=['POST', 'OPTIONS'])
def create_team():
    if request.method == 'OPTIONS':
        # CORS Preflight explizit beantworten
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    try:
        data = request.json
        if not data or 'name' not in data or not data['name']:
            return jsonify({'error': 'Teamname fehlt!'}), 400
        team = Team(name=data['name'])
        db.session.add(team)
        db.session.commit()
        return jsonify({'message': 'Team created', 'team_id': team.id}), 201
    except Exception as e:
        return jsonify({'error': f'Fehler beim Erstellen des Teams: {str(e)}'}), 500

@team_bp.route('/join', methods=['POST'])
def join_team():
    data = request.json
    user = User.query.get(data['user_id'])
    team = Team.query.get(data['team_id'])
    if not user or not team:
        return jsonify({'message': 'User or team not found'}), 404
    user.team_id = team.id
    db.session.commit()
    return jsonify({'message': 'User added to team'})

@team_bp.route('/<int:team_id>/ablage', methods=['GET'])
def get_team_ablage(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    return jsonify({'ablage': team.ablage or ""})

@team_bp.route('/<int:team_id>/ablage', methods=['POST'])
def set_team_ablage(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    data = request.json or request.form
    ablage = data.get('ablage', '')
    team.ablage = ablage
    db.session.commit()
    return jsonify({'message': 'Ablage gespeichert', 'ablage': team.ablage})

@team_bp.route('/<int:team_id>/files', methods=['GET'])
def list_team_files(team_id):
    files = load_files_metadata(team_id)
    return jsonify({'files': files})

@team_bp.route('/<int:team_id>/upload', methods=['POST'])
def upload_team_file(team_id):
    file = request.files['file']
    uploader = request.form.get('uploader') or request.form.get('user_id') or "unbekannt"
    # Username aus DB holen, falls nur user_id übergeben wird
    if uploader.isdigit():
        user = User.query.get(int(uploader))
        uploader = user.username if user else f"User {uploader}"
    if file:
        filename = secure_filename(file.filename)
        team_folder = os.path.join(UPLOAD_FOLDER, str(team_id))
        os.makedirs(team_folder, exist_ok=True)
        file.save(os.path.join(team_folder, filename))
        # Metadaten speichern
        files = load_files_metadata(team_id)
        files.append({
            "filename": filename,
            "uploader": uploader,
            "uploaded_at": datetime.utcnow().isoformat()
        })
        save_files_metadata(team_id, files)
        return jsonify({"message": "Datei hochgeladen."})
    return jsonify({"error": "Keine Datei erhalten."}), 400

@team_bp.route('/<int:team_id>/files/<filename>', methods=['GET'])
def download_team_file(team_id, filename):
    team_folder = os.path.join(UPLOAD_FOLDER, str(team_id))
    return send_from_directory(team_folder, filename, as_attachment=True)

@team_bp.route('/all', methods=['GET'])
def get_all_teams():
    teams = Team.query.all()
    return jsonify([{'id': t.id, 'name': t.name} for t in teams])
