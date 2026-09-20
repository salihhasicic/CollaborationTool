from pathlib import Path
from uuid import uuid4
from flask import Blueprint, request, jsonify, send_from_directory, g, abort, current_app
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from models import Team, User, Project, Message, TeamFile
from extensions import db
from security import data, text, integer, team_access, utc_iso

team_bp = Blueprint('team', __name__)

@team_bp.route('/create', methods=['POST'])
def create_team():
    team = Team(name=text(data().get('name', ''), 'Teamname', 100, True), owner_id=g.user.id)
    db.session.add(team)
    db.session.commit()
    return jsonify(message='Team erstellt.', team_id=team.id, name=team.name), 201

@team_bp.route('/join', methods=['POST'])
def join_team():
    body = data()
    team = team_access(integer(body.get('team_id')))
    user = db.get_or_404(User, integer(body.get('user_id')))
    user.team_id = team.id
    db.session.commit()
    return jsonify(message='Mitglied hinzugefügt.')

@team_bp.route('/<int:team_id>')
def get_team(team_id):
    team = team_access(team_id)
    return jsonify(id=team.id, name=team.name)

@team_bp.route('/<int:team_id>/ablage', methods=['GET', 'POST'])
def team_notes(team_id):
    team = team_access(team_id)
    if request.method == 'POST':
        body = data() if request.is_json else request.form
        team.ablage = text(body.get('ablage', ''), 'Notiz', 50000)
        db.session.commit()
    return jsonify(message='Notiz gespeichert.', ablage=team.ablage or '')

@team_bp.route('/<int:team_id>/files')
def list_team_files(team_id):
    team_access(team_id)
    return jsonify(files=[{'filename': f.filename, 'storage_name': f.storage_name, 'uploader': f.uploader,
                           'uploaded_at': utc_iso(f.uploaded_at)}
                          for f in TeamFile.query.filter_by(team_id=team_id).order_by(TeamFile.id)])

@team_bp.route('/<int:team_id>/upload', methods=['POST'])
def upload_team_file(team_id):
    team_access(team_id)
    file = request.files.get('file')
    filename = secure_filename(file.filename) if file and file.filename else ''
    if not filename or len(filename) > 200:
        abort(400, description='Bitte eine Datei mit einem gültigen Namen auswählen.')
    # Each upload is a separate version. Original display names may coincide.
    storage_name = f'{uuid4().hex}_{filename}'
    folder = Path(current_app.root_path) / 'uploads' / str(team_id)
    folder.mkdir(parents=True, exist_ok=True)
    file.save(folder / storage_name)
    entry = TeamFile(team_id=team_id, filename=filename, storage_name=storage_name, uploader=g.user.username)
    db.session.add(entry)
    db.session.commit()
    return jsonify(message='Datei hochgeladen.', storage_name=storage_name)

@team_bp.route('/<int:team_id>/files/<filename>')
def download_team_file(team_id, filename):
    team_access(team_id)
    entry = TeamFile.query.filter_by(team_id=team_id, storage_name=filename).first_or_404()
    folder = Path(current_app.root_path) / 'uploads' / str(team_id)
    return send_from_directory(folder, entry.storage_name, as_attachment=True, download_name=entry.filename)

@team_bp.route('/all')
def get_all_teams():
    query = Team.query
    if g.user:
        query = query.filter(or_(Team.id == g.user.team_id, Team.owner_id == g.user.id))
    return jsonify([{'id': team.id, 'name': team.name} for team in query.order_by(Team.id)])

@team_bp.route('/<int:team_id>', methods=['DELETE'])
def delete_team_backend(team_id):
    team = team_access(team_id)
    if (User.query.filter_by(team_id=team_id).first() or Project.query.filter_by(team_id=team_id).first()
            or Message.query.filter_by(team_id=team_id).first() or TeamFile.query.filter_by(team_id=team_id).first()
            or team.ablage):
        abort(409, description='Dieses Team enthält noch Mitglieder oder Daten und kann deshalb nicht gelöscht werden.')
    db.session.delete(team)
    db.session.commit()
    return jsonify(message='Team gelöscht.')
