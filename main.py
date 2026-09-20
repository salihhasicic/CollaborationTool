import os
import secrets
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, make_response, Response, jsonify, g, abort
from werkzeug.exceptions import HTTPException
import requests

app = Flask(__name__)
secret_file = Path(app.instance_path) / 'session-secret'
secret_file.parent.mkdir(parents=True, exist_ok=True)
try:
    with secret_file.open('x') as file:
        os.chmod(secret_file, 0o600)
        file.write(secrets.token_hex(32))
except FileExistsError:
    pass
app.secret_key = os.environ.get('SESSION_SECRET_KEY') or secret_file.read_text().strip()
app.config.update(MAX_CONTENT_LENGTH=20 * 1024 * 1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://127.0.0.1:5001').rstrip('/')


def backend(method, path, **kwargs):
    headers = kwargs.pop('headers', {})
    token = request.cookies.get('jwt_token')
    if token and request.endpoint not in ('login', 'register'):
        headers['Authorization'] = f'Bearer {token}'
    try:
        return requests.request(method, BACKEND_URL + path, headers=headers, timeout=20, **kwargs)
    except requests.RequestException:
        abort(503, description='Das Backend ist momentan nicht erreichbar. Bitte später erneut versuchen.')


def api(method, path, **kwargs):
    response = backend(method, path, **kwargs)
    if not response.ok:
        try:
            body = response.json()
            message = body.get('message') or body.get('error') or 'Die Anfrage konnte nicht ausgeführt werden.'
        except ValueError:
            message = 'Die Anfrage konnte nicht ausgeführt werden.'
        abort(response.status_code, description=message)
    return response.json()


def json_request():
    return request.is_json or request.path.startswith(('/api/', '/chat/private/'))


@app.before_request
def authenticate():
    # Browser mutations must originate from this site; API credentials never cross origins.
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        origin = request.headers.get('Origin')
        if request.headers.get('Sec-Fetch-Site') == 'cross-site' or (origin and origin != request.host_url.rstrip('/')):
            abort(403, description='Diese Anfrage stammt von einer anderen Website.')
    if request.endpoint in ('static', 'index', 'login', 'register', 'logout') or request.endpoint is None:
        return
    if not session.get('user_id') or not request.cookies.get('jwt_token'):
        if json_request():
            abort(401, description='Bitte zuerst einloggen.')
        return redirect(url_for('login'))
    result = backend('GET', '/auth/me')
    if result.status_code == 401:
        session.clear()
        response = make_response(jsonify(message='Bitte erneut einloggen.'), 401) if json_request() else make_response(redirect(url_for('login')))
        response.delete_cookie('jwt_token')
        return response
    if not result.ok:
        abort(503, description='Deine Sitzung konnte nicht geprüft werden. Bitte später erneut versuchen.')
    g.user = result.json()
    if g.user['user_id'] != session['user_id']:
        session.clear()
        abort(401, description='Bitte erneut einloggen.')


@app.after_request
def private_cache(response):
    if request.endpoint != 'static':
        response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    return response


@app.context_processor
def context():
    current = getattr(g, 'user', {})
    return {'backend_url': '/api', 'logged_in': bool(session.get('user_id')),
            'user_id': session.get('user_id'), 'team_id': current.get('team_id')}


@app.errorhandler(HTTPException)
def error_page(error):
    if json_request():
        return jsonify(message=error.description, error=error.description), error.code
    return render_template('error.html', message=error.description, status=error.code), error.code


@app.route('/')
def index():
    return redirect(url_for('dashboard' if session.get('user_id') else 'login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', logged_in=False)
    body = request.get_json(silent=True) if request.is_json else request.form
    if not isinstance(body, dict) and request.is_json:
        abort(400, description='Bitte Benutzername und Passwort angeben.')
    body = body or {}
    response = backend('POST', '/auth/login', json={'username': body.get('username', ''), 'password': body.get('password', '')})
    result = response.json()
    if not response.ok:
        if request.is_json:
            return jsonify(result), response.status_code
        return render_template('login.html', error=result.get('message'), logged_in=False), response.status_code
    session.clear()
    session['user_id'] = result['user_id']
    response = make_response(jsonify(result) if request.is_json else redirect(url_for('dashboard')))
    response.set_cookie('jwt_token', result['access_token'], httponly=True, samesite='Lax', secure=request.is_secure)
    return response


@app.route('/logout')
def logout():
    if request.cookies.get('jwt_token'):
        try:
            backend('POST', '/auth/logout')
        except HTTPException:
            pass
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('jwt_token')
    return response


@app.route('/api/<path:path>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def proxy_api(path):
    if path.split('/')[0] not in ('user', 'team', 'chat', 'project', 'projects', 'task'):
        abort(404)
    headers = {}
    if request.content_type:
        headers['Content-Type'] = request.content_type
    result = backend(request.method, '/' + path, params=request.args, data=request.get_data(), headers=headers)
    response = Response(result.content, status=result.status_code, content_type=result.headers.get('Content-Type'))
    if 'Content-Disposition' in result.headers:
        response.headers['Content-Disposition'] = result.headers['Content-Disposition']
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    teams = api('GET', '/team/all')
    if request.method == 'POST':
        photo = request.files.get('photo')
        files = {'photo': (photo.filename, photo.stream, photo.mimetype)} if photo and photo.filename else None
        result = backend('POST', '/auth/register', data=request.form, files=files)
        body = result.json()
        return render_template('register.html', teams=teams,
                               success='Registrierung erfolgreich! Du kannst dich jetzt einloggen.' if result.ok else None,
                               error=None if result.ok else body.get('message', 'Registrierung fehlgeschlagen.'))
    return render_template('register.html', teams=teams)


@app.route('/users')
def list_users():
    skill = request.args.get('skill', '')
    return render_template('users.html', users=api('GET', '/user/search', params={'skill': skill}), skill=skill)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    return render_template('profile.html', user=api('GET', f'/user/{user_id}'))


@app.route('/team/<int:team_id>', methods=['GET', 'POST'])
def show_team(team_id):
    api('GET', f'/team/{team_id}')
    if request.method == 'POST':
        selected = request.form.get('team_select')
        if selected:
            if not selected.isdigit():
                abort(400, description='Ungültiges Team.')
            return redirect(url_for('show_team', team_id=int(selected)))
        api('POST', f'/team/{team_id}/ablage', json={'ablage': request.form.get('ablage', '')})
        return redirect(url_for('show_team', team_id=team_id))
    users = api('GET', '/user/search', params={'skill': ''})
    return render_template('team.html', team_id=team_id, teams=api('GET', '/team/all'), all_users=users,
                           team_members=[u for u in users if u.get('team_id') == team_id],
                           ablage=api('GET', f'/team/{team_id}/ablage')['ablage'])


@app.route('/team/add', methods=['POST'])
def add_to_team():
    api('POST', '/team/join', json={'user_id': request.form.get('user_id'), 'team_id': request.form.get('team_id')})
    return redirect(url_for('show_team', team_id=int(request.form['team_id'])))


@app.route('/team_manage')
def team_manage():
    return render_template('team_manage.html')


@app.route('/teams/new')
def create_team_view():
    return render_template('create_team.html')


@app.route('/team/delete', methods=['POST'])
def delete_team():
    value = request.form.get('team_id', '')
    if not value.isdigit():
        abort(400, description='Ungültiges Team.')
    api('DELETE', f'/team/{value}')
    return redirect(url_for('team_manage'))


@app.route('/chat/<int:team_id>', methods=['GET', 'POST'])
def chat(team_id):
    api('GET', f'/team/{team_id}')
    if request.method == 'POST':
        if request.is_json:
            return jsonify(api('POST', '/chat/suggest', json=request.get_json()))
        api('POST', '/chat/send', json={'team_id': team_id, 'content': request.form.get('message', '')})
        return redirect(url_for('chat', team_id=team_id))
    return render_template('chat.html', team_id=team_id, messages=api('GET', f'/chat/team/{team_id}'), teams=api('GET', '/team/all'))


@app.route('/chats')
def chats():
    return render_template('chats.html', users=api('GET', '/user/search', params={'skill': ''}), current_user_id=session['user_id'])


@app.route('/private_chat/<int:partner_id>')
def private_chat(partner_id):
    partner = api('GET', f'/user/{partner_id}')
    return render_template('private_chat.html', partner_id=partner_id, partner_name=partner['username'])


@app.route('/chat/private/send', methods=['POST'])
def proxy_private_send():
    return jsonify(api('POST', '/chat/private/send', json=request.get_json()))


@app.route('/chat/private/<int:user1_id>/<int:user2_id>')
def proxy_private_get(user1_id, user2_id):
    return jsonify(api('GET', f'/chat/private/{user1_id}/{user2_id}'))


@app.route('/projects')
def projects():
    return render_template('projects.html', projects=api('GET', '/projects'))


@app.route('/projects/new', methods=['GET', 'POST'])
def create_project_view():
    if request.method == 'POST':
        api('POST', '/project', json={'name': request.form.get('name', ''), 'team_id': g.user['team_id'], 'deadline': request.form.get('deadline')})
        return redirect(url_for('projects'))
    return render_template('create_project.html')


@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = api('GET', f'/project/{project_id}')
    team = api('GET', f'/team/{project["team_id"]}')
    tasks = api('GET', f'/project/{project_id}/tasks')
    names = {u['id']: u['username'] for u in api('GET', '/user/search', params={'skill': ''})}
    return render_template('project_detail.html', project=project, project_id=project_id, team_name=team['name'], tasks=tasks, assigned_usernames=names)


def create_task(project_id):
    return api('POST', f'/project/{project_id}/task', json={key: request.form.get(key, '') for key in ('title', 'description', 'deadline')})


@app.route('/project/<int:project_id>/tasks/new', methods=['GET', 'POST'])
def create_task_view(project_id):
    api('GET', f'/project/{project_id}')
    if request.method == 'POST':
        create_task(project_id)
        return redirect(url_for('project_detail', project_id=project_id))
    return render_template('create_task.html', project_id=project_id)


@app.route('/tasks/new', methods=['GET', 'POST'])
def create_general_task_view():
    if request.method == 'POST':
        project_id = request.form.get('project_id', '')
        if not project_id.isdigit():
            abort(400, description='Bitte ein Projekt auswählen.')
        create_task(int(project_id))
        return redirect(url_for('dashboard'))
    return render_template('create_general_task.html', projects=api('GET', '/projects'))


@app.route('/task/<int:task_id>/move', methods=['POST'])
def move_task(task_id):
    task = api('PATCH', f'/task/{task_id}/status', json={'status': request.form.get('status')})
    return redirect(url_for('project_detail', project_id=task['project_id']))


@app.route('/task/<int:task_id>/assign', methods=['POST'])
def assign_task_view(task_id):
    api('POST', f'/task/{task_id}/assign')
    tasks = api('GET', f'/user/{session["user_id"]}/tasks')
    task = next(t for t in tasks if t['id'] == task_id)
    return redirect(url_for('project_detail', project_id=task['project_id']))


@app.route('/task/<int:task_id>/update_deadline', methods=['POST'])
def update_task_deadline(task_id):
    task = api('PATCH', f'/task/{task_id}/deadline', json={'deadline': request.form.get('deadline')})
    return redirect(url_for('project_detail', project_id=task['project_id']))


@app.route('/project/<int:project_id>/update_deadline', methods=['POST'])
def update_project_deadline_view(project_id):
    api('PATCH', f'/project/{project_id}/deadline', json={'deadline': request.form.get('deadline')})
    return redirect(url_for('project_detail', project_id=project_id))


@app.route('/start')
def dashboard():
    user = api('GET', f'/user/{session["user_id"]}')
    projects = api('GET', '/projects')
    tasks = api('GET', f'/user/{user["id"]}/tasks')
    priority = lambda item: (item.get('deadline') or '9999', item['id'])
    open_tasks = [t for t in tasks if t['status'] != 'Done']
    open_projects = [p for p in projects if p['status'] != 'Done']
    progress_projects = sorted(projects, key=priority)[:3]
    for project in progress_projects:
        project_tasks = api('GET', f'/project/{project["id"]}/tasks')
        project['progress'] = round(100 * sum(t['status'] == 'Done' for t in project_tasks) / len(project_tasks)) if project_tasks else 0
    return render_template('dashboard.html', user=user, tasks=sorted(open_tasks, key=priority)[:3],
                           projects=sorted(open_projects, key=priority)[:3], progress_projects=progress_projects,
                           open_task_count=len(open_tasks), closed_task_count=len(tasks)-len(open_tasks))


if __name__ == '__main__':
    app.run(port=3000, debug=True)
