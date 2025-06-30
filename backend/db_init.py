from app import app
from extensions import db
from models import User, Team
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    team1 = Team(name='Dev Team')
    db.session.add(team1)
    db.session.commit()

    db.session.add(User(
        username="alice",
        password=generate_password_hash("1234"),
        photo_url="https://example.com/photo.jpg",
        location="Zürich",
        skills="Python,Flask",
        latitude=47.3769,
        longitude=8.5417,
        team_id=team1.id
    ))
    db.session.add(User(
        username="bob",
        password=generate_password_hash("5678"),
        photo_url="https://example.com/photo.jpg",
        location="Bern",
        skills="JavaScript,Vue",
        latitude=46.9481,
        longitude=7.4474,
        team_id=team1.id
    ))
    db.session.add(User(
        username="carla",
        password=generate_password_hash("pass123"),
        photo_url="https://example.com/photo.jpg",
        location="Winterthur",
        skills="Java,Spring",
        latitude=47.4988,
        longitude=8.7237,
        team_id=team1.id
    ))
    db.session.add(User(
        username="daniel",
        password=generate_password_hash("hello123"),
        photo_url="https://example.com/photo.jpg",
        location="Basel",
        skills="Python,Data Science",
        latitude=47.5596,
        longitude=7.5886,
        team_id=team1.id
    ))
    db.session.add(User(
        username="elena",
        password=generate_password_hash("qwertz"),
        photo_url="https://example.com/photo.jpg",
        location="Luzern",
        skills="C#,Unity",
        latitude=47.0502,
        longitude=8.3093,
        team_id=team1.id
    ))
    db.session.add(User(
        username="fritz",
        password=generate_password_hash("passwort"),
        photo_url="https://example.com/photo.jpg",
        location="St. Gallen",
        skills="Kotlin,Android",
        latitude=47.4245,
        longitude=9.3767,
        team_id=team1.id
    ))
    db.session.commit()
    print("✅ Dummy-User mit Geo-Daten hinzugefügt.")
