from flask import Blueprint, request, jsonify, send_from_directory, current_app
from models import Team, User
from extensions import db
import os

team_bp = Blueprint('team', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

@team_bp.route('/create', methods=['POST'])
def create_team():
    data = request.json
    team = Team(name=data['name'])
    db.session.add(team)
    db.session.commit()
    return jsonify({'message': 'Team created', 'team_id': team.id})

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
    team_folder = os.path.join(UPLOAD_FOLDER, f"team_{team_id}")
    if not os.path.exists(team_folder):
        return jsonify({'files': []})
    files = os.listdir(team_folder)
    return jsonify({'files': files})

@team_bp.route('/<int:team_id>/upload', methods=['POST'])
def upload_team_file(team_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    team_folder = os.path.join(UPLOAD_FOLDER, f"team_{team_id}")
    os.makedirs(team_folder, exist_ok=True)
    file.save(os.path.join(team_folder, file.filename))
    return jsonify({'message': 'File uploaded'})

@team_bp.route('/<int:team_id>/files/<filename>', methods=['GET'])
def download_team_file(team_id, filename):
    team_folder = os.path.join(UPLOAD_FOLDER, f"team_{team_id}")
    return send_from_directory(team_folder, filename, as_attachment=True)
