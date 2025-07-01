from flask import Flask, render_template, request, redirect, url_for, session
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f'{BACKEND_URL}/auth/login', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            user_id = response.json()['user_id']
            session['user_id'] = user_id
            return redirect(url_for('list_users'))
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
    response = requests.get(f'{BACKEND_URL}/user/{user_id}')
    if response.status_code == 200:
        user = response.json()
        return render_template('profile.html', user=user, logged_in='user_id' in session)
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
        response = requests.post(f'{BACKEND_URL}/auth/register', json={
            'username': username,
            'password': password,
            'team_id': team_id,
            'skills': skills,
            'location': location,
            'latitude': latitude,
            'longitude': longitude
        })
        if response.status_code == 201:
            return render_template('register.html', success="Registrierung erfolgreich! Du kannst dich jetzt einloggen.", teams=teams)
        else:
            error = response.json().get('message', 'Registrierung fehlgeschlagen.')
            return render_template('register.html', error=error, teams=teams)
    return render_template('register.html', teams=teams)

if __name__ == '__main__':
    app.run(port=3000, debug=True)
