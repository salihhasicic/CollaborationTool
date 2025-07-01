from flask import Blueprint, request, jsonify
from extensions import db
from models import Project, Task, Team, User
from flask_jwt_extended import jwt_required, get_jwt_identity

project_bp = Blueprint('project', __name__)

# Hilfsfunktion: Team-Zugehörigkeit prüfen
def user_in_team(user_id, team_id):
    user = User.query.get(user_id)
    return user and user.team_id == team_id

# Projekt anlegen
@project_bp.route('/project', methods=['POST'])
@jwt_required()
def create_project():
    data = request.json
    user_id = get_jwt_identity()
    team_id = data.get('team_id')
    if not user_in_team(user_id, team_id):
        return jsonify({'error': 'Kein Zugriff auf dieses Team'}), 403
    project = Project(name=data['name'], status=data.get('status', 'To Do'), team_id=team_id)
    db.session.add(project)
    db.session.commit()
    return jsonify({'id': project.id, 'name': project.name, 'status': project.status, 'team_id': project.team_id})

# Projekte des eigenen Teams anzeigen
@project_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    projects = Project.query.filter_by(team_id=user.team_id).all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'status': p.status, 'team_id': p.team_id} for p in projects
    ])

# Projekt-Status ändern
@project_bp.route('/project/<int:project_id>/status', methods=['PATCH'])
@jwt_required()
def update_project_status(project_id):
    data = request.json
    user_id = get_jwt_identity()
    project = Project.query.get_or_404(project_id)
    if not user_in_team(user_id, project.team_id):
        return jsonify({'error': 'Kein Zugriff auf dieses Projekt'}), 403
    project.status = data['status']
    db.session.commit()
    return jsonify({'id': project.id, 'status': project.status})

# Hilfsfunktion: Projektstatus neu berechnen
def recalc_project_status(project):
    tasks = Task.query.filter_by(project_id=project.id).all()
    if not tasks:
        return "To Do"
    statuses = [t.status for t in tasks]
    if all(s == "Done" for s in statuses):
        return "Done"
    if all(s == "To Do" for s in statuses):
        return "To Do"
    return "In Progress"

# Task anlegen
@project_bp.route('/project/<int:project_id>/task', methods=['POST'])
@jwt_required()
def create_task(project_id):
    data = request.json
    user_id = get_jwt_identity()
    project = Project.query.get_or_404(project_id)
    if not user_in_team(user_id, project.team_id):
        return jsonify({'error': 'Kein Zugriff auf dieses Projekt'}), 403
    task = Task(title=data['title'], description=data.get('description', ''), status=data.get('status', 'To Do'), project_id=project_id)
    db.session.add(task)
    db.session.commit()
    # Nach Anlegen: Projektstatus neu berechnen
    project.status = recalc_project_status(project)
    db.session.commit()
    return jsonify({'id': task.id, 'title': task.title, 'status': task.status, 'project_id': task.project_id, 'project_status': project.status})

# Tasks eines Projekts anzeigen
@project_bp.route('/project/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(project_id):
    user_id = get_jwt_identity()
    project = Project.query.get_or_404(project_id)
    if not user_in_team(user_id, project.team_id):
        return jsonify({'error': 'Kein Zugriff auf dieses Projekt'}), 403
    tasks = Task.query.filter_by(project_id=project_id).all()
    return jsonify([
        {'id': t.id, 'title': t.title, 'description': t.description, 'status': t.status, 'project_id': t.project_id, 'assigned_user_id': t.assigned_user_id} for t in tasks
    ])

# Task-Status ändern (z.B. für Kanban-Board)
@project_bp.route('/task/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    data = request.json
    user_id = get_jwt_identity()
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    if not user_in_team(user_id, project.team_id):
        return jsonify({'error': 'Kein Zugriff auf dieses Projekt'}), 403
    task.status = data['status']
    db.session.commit()
    # Nach Status-Änderung: Projektstatus neu berechnen
    project.status = recalc_project_status(project)
    db.session.commit()
    return jsonify({'id': task.id, 'status': task.status, 'project_status': project.status})

# Task zuweisen (nur an sich selbst, wenn noch nicht zugewiesen)
@project_bp.route('/task/<int:task_id>/assign', methods=['POST'])
@jwt_required()
def assign_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    if not user_in_team(user_id, project.team_id):
        return jsonify({'error': 'Kein Zugriff auf dieses Projekt'}), 403
    if task.assigned_user_id is not None:
        return jsonify({'error': 'Task ist bereits zugewiesen'}), 400
    task.assigned_user_id = user_id
    db.session.commit()
    return jsonify({'id': task.id, 'assigned_user_id': task.assigned_user_id})

@project_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'username': user.username})
