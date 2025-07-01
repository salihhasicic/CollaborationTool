from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

BACKEND_URL = 'http://127.0.0.1:5000'  # Passe den Port ggf. an

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask import make_response
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f'{BACKEND_URL}/auth/login', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            data = response.json()
            user_id = data['user_id']
            access_token = data.get('access_token')
            resp = make_response(redirect(url_for('profile', user_id=user_id)))
            if access_token:
                resp.set_cookie('jwt_token', access_token)
            return resp
        else:
            return render_template('login.html', error="Login fehlgeschlagen.")
    return render_template('login.html')

@app.route('/users')
def list_users():
    skill = request.args.get('skill', '')
    response = requests.get(f'{BACKEND_URL}/user/search', params={'skill': skill})
    if response.status_code == 200:
        users = response.json()
        return render_template('users.html', users=users, skill=skill)
    else:
        return "Fehler beim Laden der Benutzer", 500

@app.route('/team/<int:team_id>', methods=['GET', 'POST'])
def show_team(team_id):
    # Ablage speichern (POST)
    if request.method == 'POST':
        ablage = request.form.get('ablage', '')
        res = requests.post(f'{BACKEND_URL}/team/{team_id}/ablage', data={'ablage': ablage})
        # Fehlerbehandlung ignoriert, da wir gleich neu laden

    # Hole alle User und filtere nach Team-ID
    response = requests.get(f'{BACKEND_URL}/user/search', params={'skill': ''})
    ablage = ""
    ablage_res = requests.get(f'{BACKEND_URL}/team/{team_id}/ablage')
    if ablage_res.status_code == 200:
        ablage = ablage_res.json().get('ablage', '')
    if response.status_code == 200:
        all_users = response.json()
        team_members = [u for u in all_users if u.get('team_id') == team_id]
        return render_template('team.html', team_id=team_id, team_members=team_members, ablage=ablage)
    else:
        return "Fehler beim Laden des Teams", 500

@app.route('/team/add', methods=['POST'])
def add_to_team():
    user_id = request.form.get('user_id')
    team_id = request.form.get('team_id') or 1
    response = requests.post(f'{BACKEND_URL}/team/join', json={
        'user_id': int(user_id),
        'team_id': int(team_id)
    })
    if response.status_code == 200:
        return redirect(url_for('show_team', team_id=team_id))
    else:
        return "Fehler beim Hinzufügen", 500

@app.route('/chat/<int:team_id>', methods=['GET', 'POST'])
def chat(team_id):
    if request.method == 'POST':
        message = request.form['message']
        sender_id = request.form['sender_id']
        response = requests.post(f'{BACKEND_URL}/chat/send', json={
            'sender_id': int(sender_id),
            'team_id': team_id,
            'content': message
        })
        if response.status_code != 200:
            return "Fehler beim Senden", 500

    res = requests.get(f'{BACKEND_URL}/chat/team/{team_id}')
    if res.status_code == 200:
        messages = res.json()
        # Hier backend_url übergeben!
        return render_template('chat.html', messages=messages, team_id=team_id, backend_url=BACKEND_URL)
    else:
        return "Fehler beim Laden der Nachrichten", 500

@app.route('/profile/<int:user_id>')
def profile(user_id):
    response = requests.get(f'{BACKEND_URL}/user/{user_id}')
    if response.status_code == 200:
        user = response.json()
        return render_template('profile.html', user=user)
    else:
        return "Benutzer nicht gefunden", 404

@app.route('/projects')
def projects():
    token = request.cookies.get('jwt_token')
    print('DEBUG JWT_TOKEN:', token)
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    response = requests.get(f'{BACKEND_URL}/projects', headers=headers)
    if response.status_code == 200:
        projects = response.json()
        return render_template('projects.html', projects=projects)
    else:
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text
        return f"Fehler beim Laden der Projekte (Status: {response.status_code}): {error_msg}", 500

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    # Projekt-Infos laden
    project_response = requests.get(f'{BACKEND_URL}/projects', headers=headers)
    project = None
    team_name = None
    if project_response.status_code == 200:
        projects = project_response.json()
        for p in projects:
            if p['id'] == project_id:
                project = p
                break
        if project:
            # Team-Name laden
            team_id = project.get('team_id')
            if team_id:
                team_response = requests.get(f'{BACKEND_URL}/team/{team_id}')
                if team_response.status_code == 200:
                    team = team_response.json()
                    team_name = team.get('name')
    # Tasks laden
    response = requests.get(f'{BACKEND_URL}/project/{project_id}/tasks', headers=headers)
    assigned_usernames = {}
    if response.status_code == 200:
        tasks = response.json()
        # Usernamen für zugewiesene Tasks holen
        for t in tasks:
            uid = t.get('assigned_user_id')
            if uid and uid not in assigned_usernames:
                user_response = requests.get(f'{BACKEND_URL}/user/{uid}')
                if user_response.status_code == 200:
                    assigned_usernames[uid] = user_response.json().get('username')
                else:
                    assigned_usernames[uid] = f"User {uid}"
        return render_template('project_detail.html', tasks=tasks, project_id=project_id, project=project, team_name=team_name, assigned_usernames=assigned_usernames)
    else:
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text
        return f"Fehler beim Laden der Tasks (Status: {response.status_code}): {error_msg}", 500

@app.route('/projects/new', methods=['GET', 'POST'])
def create_project_view():
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    # Team-ID automatisch aus dem eingeloggten User holen
    user_id = None
    if token:
        import jwt
        try:
            # JWT-Token dekodieren, um User-ID zu bekommen
            payload = jwt.decode(token, options={"verify_signature": False})
            user_id = payload.get('sub')
        except Exception:
            user_id = None
    # Team-ID vom User holen
    team_id = None
    if user_id:
        user_response = requests.get(f'{BACKEND_URL}/user/{user_id}')
        if user_response.status_code == 200:
            user = user_response.json()
            team_id = user.get('team_id')
    if request.method == 'POST':
        name = request.form['name']
        # Team-ID automatisch verwenden
        data = {'name': name, 'team_id': team_id}
        response = requests.post(f'{BACKEND_URL}/project', json=data, headers=headers)
        if response.status_code == 200:
            return redirect(url_for('projects'))
        else:
            try:
                error_msg = response.json()
            except Exception:
                error_msg = response.text
            return f"Fehler beim Anlegen des Projekts (Status: {response.status_code}): {error_msg}", 500
    return render_template('create_project.html', team_id=team_id)

@app.route('/project/<int:project_id>/tasks/new', methods=['GET', 'POST'])
def create_task_view(project_id):
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        data = {'title': title, 'description': description}
        response = requests.post(f'{BACKEND_URL}/project/{project_id}/task', json=data, headers=headers)
        if response.status_code == 200:
            return redirect(url_for('project_detail', project_id=project_id))
        else:
            return "Fehler beim Anlegen des Tasks", 500
    return render_template('create_task.html', project_id=project_id)

@app.route('/task/<int:task_id>/move', methods=['POST'])
def move_task(task_id):
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    new_status = request.form['status']
    data = {'status': new_status}
    response = requests.patch(f'{BACKEND_URL}/task/{task_id}/status', json=data, headers=headers)
    if response.status_code == 200:
        # Hole das Projekt zu diesem Task (vereinfachte Annahme: project_id kommt als hidden field)
        project_id = request.form['project_id']
        return redirect(url_for('project_detail', project_id=project_id))
    else:
        return "Fehler beim Verschieben des Tasks", 500

@app.route('/task/<int:task_id>/assign', methods=['POST'])
def assign_task_view(task_id):
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    response = requests.post(f'{BACKEND_URL}/task/{task_id}/assign', headers=headers)
    # Hole das Projekt zu diesem Task (vereinfachte Annahme: project_id kommt als hidden field oder redirect zurück)
    if response.status_code == 200:
        # Projekt-ID aus Referer oder Task-Detail holen
        referer = request.headers.get('Referer')
        if referer and '/project/' in referer:
            try:
                project_id = int(referer.split('/project/')[1].split('/')[0])
                return redirect(url_for('project_detail', project_id=project_id))
            except Exception:
                pass
        return redirect(url_for('projects'))
    else:
        try:
            error_msg = response.json()
        except Exception:
            error_msg = response.text
        return f"Fehler beim Übernehmen des Tasks (Status: {response.status_code}): {error_msg}", 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
