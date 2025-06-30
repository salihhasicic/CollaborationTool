from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

BACKEND_URL = 'http://localhost:5000'  # Passe den Port ggf. an

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        response = requests.post(f'{BACKEND_URL}/login', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            user_id = response.json()['user_id']
            return redirect(url_for('profile', user_id=user_id))
        else:
            return render_template('login.html', error="Login fehlgeschlagen.")
    return render_template('login.html')

@app.route('/users')
def list_users():
    skill = request.args.get('skill', '')
    response = requests.get(f'{BACKEND_URL}/search', params={'skill': skill})
    if response.status_code == 200:
        users = response.json()
        return render_template('users.html', users=users, skill=skill)
    else:
        return "Fehler beim Laden der Benutzer", 500

@app.route('/team/<int:team_id>')
def show_team(team_id):
    response = requests.get(f'{BACKEND_URL}/search')  # alle User
    if response.status_code == 200:
        all_users = response.json()
        team_members = [u for u in all_users if u['team_id'] == team_id]
        return render_template('team.html', team_id=team_id, team_members=team_members)
    else:
        return "Fehler beim Laden des Teams", 500

@app.route('/team/add', methods=['POST'])
def add_to_team():
    user_id = request.form.get('user_id')
    team_id = request.form.get('team_id') or 1  # Standardteam für Demo
    response = requests.post(f'{BACKEND_URL}/team/add_user', json={
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
            'message': message
        })
        if response.status_code != 200:
            return "Fehler beim Senden", 500

    # Nachrichten laden
    res = requests.get(f'{BACKEND_URL}/chat/{team_id}')
    if res.status_code == 200:
        messages = res.json()
        return render_template('chat.html', messages=messages, team_id=team_id)
    else:
        return "Fehler beim Laden der Nachrichten", 500


@app.route('/profile/<int:user_id>')
def profile(user_id):
    response = requests.get(f'{BACKEND_URL}/{user_id}')
    if response.status_code == 200:
        user = response.json()
        return render_template('profile.html', user=user)
    else:
        return "Benutzer nicht gefunden", 404

if __name__ == '__main__':
    app.run(port=3000, debug=True)
