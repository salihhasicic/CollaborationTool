from flask import Blueprint, jsonify, g, abort
from extensions import db
from models import Project, Task, User
from security import data, text, integer, team_access, status, deadline, utc_iso

project_bp = Blueprint('project', __name__)

def project_access(project_id):
    project = db.get_or_404(Project, project_id)
    team_access(project.team_id)
    return project

def task_access(task_id, edit=False):
    task = db.get_or_404(Task, task_id)
    project_access(task.project_id)
    if edit and task.assigned_user_id != g.user.id:
        abort(403, description='Nur die verantwortliche Person kann diese Aufgabe ändern.')
    return task

def serialize_project(p):
    return {'id': p.id, 'name': p.name, 'status': p.status, 'team_id': p.team_id, 'deadline': utc_iso(p.deadline)}

def serialize_task(t):
    return {'id': t.id, 'title': t.title, 'description': t.description, 'status': t.status,
            'project_id': t.project_id, 'assigned_user_id': t.assigned_user_id, 'deadline': utc_iso(t.deadline)}

def recalc_project_status(project):
    db.session.flush()
    tasks = Task.query.filter_by(project_id=project.id).all()
    states = [t.status for t in tasks]
    project.status = ('Done' if states and all(s == 'Done' for s in states)
                      else 'To Do' if all(s == 'To Do' for s in states) else 'In Progress')

@project_bp.route('/project', methods=['POST'])
def create_project():
    body = data()
    team = team_access(integer(body.get('team_id')))
    project = Project(name=text(body.get('name', ''), 'Projektname', 120, True), team_id=team.id,
                      status=status(body.get('status', 'To Do')), deadline=deadline(body.get('deadline')))
    db.session.add(project)
    db.session.commit()
    return jsonify(serialize_project(project))

@project_bp.route('/projects')
def get_projects():
    projects = Project.query.filter_by(team_id=g.user.team_id).all() if g.user.team_id else []
    return jsonify([serialize_project(p) for p in projects])

@project_bp.route('/project/<int:project_id>')
def get_project_by_id(project_id):
    return jsonify(serialize_project(project_access(project_id)))

@project_bp.route('/project/<int:project_id>/status', methods=['PATCH'])
def update_project_status(project_id):
    project = project_access(project_id)
    project.status = status(data().get('status'))
    db.session.commit()
    return jsonify(serialize_project(project))

@project_bp.route('/project/<int:project_id>/task', methods=['POST'])
def create_task(project_id):
    project = project_access(project_id)
    body = data()
    task = Task(title=text(body.get('title', ''), 'Aufgabentitel', 120, True),
                description=text(body.get('description', ''), 'Beschreibung'), project_id=project.id,
                status=status(body.get('status', 'To Do')), deadline=deadline(body.get('deadline')))
    db.session.add(task)
    recalc_project_status(project)
    db.session.commit()
    return jsonify(**serialize_task(task), project_status=project.status)

@project_bp.route('/project/<int:project_id>/tasks')
def get_tasks(project_id):
    project_access(project_id)
    return jsonify([serialize_task(t) for t in Task.query.filter_by(project_id=project_id).order_by(Task.id)])

@project_bp.route('/task/<int:task_id>/status', methods=['PATCH'])
def update_task_status(task_id):
    task = task_access(task_id, edit=True)
    task.status = status(data().get('status'))
    recalc_project_status(task.project)
    db.session.commit()
    return jsonify(**serialize_task(task), project_status=task.project.status)

@project_bp.route('/task/<int:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    task_access(task_id)
    changed = Task.query.filter_by(id=task_id, assigned_user_id=None).update({'assigned_user_id': g.user.id})
    if not changed:
        abort(409, description='Diese Aufgabe ist bereits vergeben.')
    db.session.commit()
    return jsonify(id=task_id, assigned_user_id=g.user.id)

@project_bp.route('/user/<int:user_id>/tasks')
def get_tasks_by_user(user_id):
    if user_id != g.user.id:
        abort(403, description='Du kannst nur deine eigenen Aufgaben abrufen.')
    return jsonify([serialize_task(t) for t in Task.query.join(Project).filter(
        Task.assigned_user_id == user_id, Project.team_id == g.user.team_id).all()])

@project_bp.route('/project/<int:project_id>/deadline', methods=['PATCH'])
def update_project_deadline(project_id):
    project = project_access(project_id)
    project.deadline = deadline(data().get('deadline'))
    db.session.commit()
    return jsonify(serialize_project(project))

@project_bp.route('/task/<int:task_id>/deadline', methods=['PATCH'])
def update_task_deadline(task_id):
    task = task_access(task_id, edit=True)
    task.deadline = deadline(data().get('deadline'))
    db.session.commit()
    return jsonify(serialize_task(task))
