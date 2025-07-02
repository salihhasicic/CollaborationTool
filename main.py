from flask import Flask, render_template, request, redirect, url_for, session, make_response 
from flask import Response
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecret"  # Für Session-Handling

BACKEND_URL = 'http://127.0.0.1:5000'  # Passe den Port ggf. an

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

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

            session['user_id'] = user_id

            resp = make_response(redirect(url_for('list_users')))
            if access_token:
                resp.set_cookie(
                    'jwt_token', access_token,
                    httponly=True, samesite='Lax'
                )
            return resp
        else:
            return render_template('login.html', error="Login fehlgeschlagen.", logged_in=False)
    return render_template('login.html', logged_in=False)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/users')
@login_required
def list_users():
    skill = request.args.get('skill', '')
    response = requests.get(f'{BACKEND_URL}/user/search', params={'skill': skill})
    team_id = None
    if 'user_id' in session:
        user_res = requests.get(f'{BACKEND_URL}/user/{session["user_id"]}')
        if user_res.status_code == 200:
            user = user_res.json()
            team_id = user.get('team_id')
    if response.status_code == 200:
        users = response.json()
        return render_template('users.html', users=users, skill=skill, logged_in=True, team_id=team_id)
    else:
        return "Fehler beim Laden der Benutzer", 500

@app.route('/team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def show_team(team_id):
    # Ablage speichern (POST)
    if request.method == 'POST':
        ablage = request.form.get('ablage', '')
        selected_team_id = request.form.get('team_select')
        if selected_team_id and int(selected_team_id) != team_id:
            return redirect(url_for('show_team', team_id=int(selected_team_id)))
        res = requests.post(f'{BACKEND_URL}/team/{team_id}/ablage', data={'ablage': ablage})

    # Hole alle Teams für Dropdown
    teams_res = requests.get(f'{BACKEND_URL}/team/all')
    teams = teams_res.json() if teams_res.status_code == 200 else []

    # Hole alle User und filtere nach Team-ID
    response = requests.get(f'{BACKEND_URL}/user/search', params={'skill': ''})
    ablage = ""
    ablage_res = requests.get(f'{BACKEND_URL}/team/{team_id}/ablage')
    if ablage_res.status_code == 200:
        ablage = ablage_res.json().get('ablage', '')
    if response.status_code == 200:
        all_users = response.json()
        team_members = [u for u in all_users if u.get('team_id') == team_id]
        return render_template('team.html', team_id=team_id, team_members=team_members, ablage=ablage, logged_in='user_id' in session, teams=teams)
    else:
        return "Fehler beim Laden des Teams", 500

@app.route('/team/add', methods=['POST'])
@login_required
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
@login_required
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
        return render_template('chat.html', messages=messages, team_id=team_id, backend_url=BACKEND_URL, logged_in='user_id' in session)
    else:
        return "Fehler beim Laden der Nachrichten", 500

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    # Lade das Profil, das angezeigt werden soll
    response = requests.get(f'{BACKEND_URL}/user/{user_id}')
    print(response.json()) 
    
    # Separat: aktuell eingeloggter Nutzer
    current_user_id = session.get('user_id')
    team_id = None

    if current_user_id:
        user_res = requests.get(f'{BACKEND_URL}/user/{current_user_id}')
        if user_res.status_code == 200:
            current_user = user_res.json()
            team_id = current_user.get('team_id')

    if response.status_code == 200:
        user = response.json()
        return render_template(
            'profile.html',
            user=user,  # angezeigtes Profil
            team_id=team_id,
            logged_in=True,
            user_id=current_user_id  # eingeloggter Nutzer
        )
    else:
        return "Benutzer nicht gefunden", 404

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Teams für Dropdown laden
    teams_res = requests.get(f'{BACKEND_URL}/team/all')
    teams = teams_res.json() if teams_res.status_code == 200 else []
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        team_id = request.form.get('team_id')
        skills = request.form.get('skills', '')
        location = request.form.get('location', '')
        latitude = request.form.get('latitude', '')
        longitude = request.form.get('longitude', '')
        photo = request.files.get('photo')


        files = {'photo': photo} if photo and photo.filename else {}

        # Formulardaten als dictionary
        data = {
            'username': username,
            'password': password,
            'team_id': team_id,
            'skills': skills,
            'location': location,
            'latitude': latitude,
            'longitude': longitude
        }

        # POST mit multipart/form-data
        response = requests.post(f'{BACKEND_URL}/auth/register', data=data, files=files)

        if response.status_code == 201:
            return render_template('register.html', success="Registrierung erfolgreich! Du kannst dich jetzt einloggen.", teams=teams)
        else:
            try:
                error = response.json().get('message', 'Registrierung fehlgeschlagen.')
            except Exception:
                error = 'Registrierung fehlgeschlagen.'
            return render_template('register.html', error=error, teams=teams)

    return render_template('register.html', teams=teams)

@app.route('/projects')
def projects():
    token = request.cookies.get('jwt_token')
    print('DEBUG JWT_TOKEN:', token)
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    response = requests.get(f'{BACKEND_URL}/projects', headers=headers)
    projects = response.json() if response.status_code == 200 else []

    # team_id über den eingeloggten Nutzer holen
    current_user_id = session.get('user_id')
    team_id = None
    if current_user_id:
        user_res = requests.get(f'{BACKEND_URL}/user/{current_user_id}')
        if user_res.status_code == 200:
            user = user_res.json()
            team_id = user.get('team_id')

    return render_template('projects.html',
                           projects=projects,
                           team_id=team_id,
                           logged_in='user_id' in session,
                           user_id=session.get('user_id'))

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
            project_team_id = project.get('team_id')
            if project_team_id:
                team_response = requests.get(f'{BACKEND_URL}/team/{project_team_id}')
                if team_response.status_code == 200:
                    team = team_response.json()
                    team_name = team.get('name')

    # Aktuellen Benutzer & Team-ID ermitteln (für Navbar)
    current_user_id = session.get('user_id')
    team_id = None
    if current_user_id:
        user_res = requests.get(f'{BACKEND_URL}/user/{current_user_id}')
        if user_res.status_code == 200:
            user = user_res.json()
            team_id = user.get('team_id')

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

        return render_template(
            'project_detail.html',
            tasks=tasks,
            project_id=project_id,
            project=project,
            team_name=team_name,
            assigned_usernames=assigned_usernames,
            team_id=team_id,
            logged_in='user_id' in session,
            user_id=session.get('user_id')
        )
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
    return render_template('create_project.html', team_id=team_id, logged_in='user_id' in session, user_id=session.get('user_id'))

@app.route('/project/<int:project_id>/tasks/new', methods=['GET', 'POST'])
def create_task_view(project_id):
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    # Aktuellen Benutzer und team_id ermitteln
    current_user_id = session.get('user_id')
    team_id = None
    if current_user_id:
        user_response = requests.get(f'{BACKEND_URL}/user/{current_user_id}')
        if user_response.status_code == 200:
            user = user_response.json()
            team_id = user.get('team_id')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        data = {'title': title, 'description': description}
        response = requests.post(f'{BACKEND_URL}/project/{project_id}/task', json=data, headers=headers)
        if response.status_code == 200:
            return redirect(url_for('project_detail', project_id=project_id))
        else:
            return "Fehler beim Anlegen des Tasks", 500

    return render_template(
        'create_task.html',
        project_id=project_id,
        team_id=team_id,
        logged_in='user_id' in session,
        user_id=session.get('user_id')
    )


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

@app.route('/private_chat/<int:partner_id>')
@login_required
def private_chat(partner_id):
    return render_template('private_chat.html')

@app.route('/chats')
def chats():
    # Alle User laden
    response = requests.get(f'{BACKEND_URL}/user/search', params={'skill': ''})
    users = response.json() if response.status_code == 200 else []
    current_user_id = session.get('user_id')
    team_id = None
    if current_user_id:
        user_res = requests.get(f'{BACKEND_URL}/user/{current_user_id}')
        if user_res.status_code == 200:
            user = user_res.json()
            team_id = user.get('team_id')
    return render_template('chats.html', users=users, current_user_id=current_user_id, team_id=team_id, logged_in='user_id' in session)

@app.route('/chat/private/send', methods=['POST'])
def proxy_private_send():
    resp = requests.post(f'{BACKEND_URL}/chat/private/send', json=request.get_json())
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

@app.route('/chat/private/<int:user1_id>/<int:user2_id>', methods=['GET'])
def proxy_private_get(user1_id, user2_id):
    resp = requests.get(f'{BACKEND_URL}/chat/private/{user1_id}/{user2_id}')
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get('Content-Type'))

@app.route('/auth/proxy-login', methods=['POST'])
def proxy_login():
    data = request.get_json()
    user_id = data.get('user_id')
    access_token = data.get('access_token')

    if not user_id or not access_token:
        return {"message": "Fehlende Daten"}, 400

    session['user_id'] = user_id
    resp = make_response({"message": "Login erfolgreich"})
    resp.set_cookie('jwt_token', access_token, httponly=True, samesite='Lax')
    return resp

@app.route('/start')
@login_required
def dashboard():
    user_id = session.get('user_id')

    # 1. Hole den eingeloggten User inkl. Team
    user_res = requests.get(f'{BACKEND_URL}/user/{user_id}')
    if user_res.status_code != 200:
        return "User konnte nicht geladen werden", 500

    user = user_res.json()
    team_id = user.get('team_id')
    if isinstance(team_id, str):
        team_id = int(team_id)

    # 2. Hole Projekte dieses Teams
    projects = []
    if team_id:
        token = request.cookies.get('jwt_token')
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        projects_res = requests.get(f'{BACKEND_URL}/projects', headers=headers)
    
        if projects_res.status_code == 200:
            all_projects = projects_res.json()


            # Nur Projekte mit der Team-ID des Users
            projects = [p for p in all_projects if p.get("team_id") == team_id]

    # 3. Hole Tasks des Users
    token = request.cookies.get('jwt_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    tasks_res = requests.get(f'{BACKEND_URL}/user/{user_id}/tasks', headers=headers)  # ✅ hier!
    print("DEBUG: Tasks response", tasks_res.status_code)

    if tasks_res.status_code == 200:
        print("DEBUG: Tasks JSON", tasks_res.json())
        tasks = tasks_res.json()
    else:
        print("DEBUG: Inhalt bei Fehler:", tasks_res.text)
        tasks = []

    return render_template('dashboard.html',
                           user=user,
                           tasks=tasks,
                           projects=projects,
                           team_id=team_id,
                           logged_in=True,
                           user_id=user_id)


if __name__ == '__main__':
    app.run(port=3000, debug=True)
