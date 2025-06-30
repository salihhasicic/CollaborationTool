from flask import Blueprint, request, jsonify
from models import Team, User
from extensions import db

team_bp = Blueprint('team', __name__)

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
