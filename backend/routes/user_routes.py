from flask import Blueprint, request, jsonify
from models import User
from extensions import db

user_bp = Blueprint('user', __name__)

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
        'team_id': user.team_id
    })

@user_bp.route('/search', methods=['GET'])
def search_users():
    skill = request.args.get('skill')
    users = User.query.filter(User.skills.like(f"%{skill}%")).all()
    result = [{'id': u.id, 'username': u.username, 'skills': u.skills} for u in users]
    return jsonify(result)
