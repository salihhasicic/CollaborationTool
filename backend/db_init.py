from app import app
from extensions import db
from models import User, Team
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    # Teams erstellen
    team1 = Team(name='Dev Team')
    team2 = Team(name='Design Team')
    team3 = Team(name='AI Team')
    db.session.add_all([team1, team2, team3])
    db.session.commit()

    db.session.add_all([
        User(username="alice", password=generate_password_hash("1234"), photo_url="https://example.com/photo.jpg", location="Zürich", skills="Python,Flask", latitude=47.3769, longitude=8.5417, team_id=team1.id),
        User(username="bob", password=generate_password_hash("5678"), photo_url="https://example.com/photo.jpg", location="Bern", skills="JavaScript,Vue", latitude=46.9481, longitude=7.4474, team_id=team1.id),
        User(username="carla", password=generate_password_hash("pass123"), photo_url="https://example.com/photo.jpg", location="Winterthur", skills="Java,Spring", latitude=47.4988, longitude=8.7237, team_id=team2.id),
        User(username="daniel", password=generate_password_hash("hello123"), photo_url="https://example.com/photo.jpg", location="Basel", skills="Python,Data Science", latitude=47.5596, longitude=7.5886, team_id=team3.id),
        User(username="elena", password=generate_password_hash("qwertz"), photo_url="https://example.com/photo.jpg", location="Luzern", skills="C#,Unity", latitude=47.0502, longitude=8.3093, team_id=team2.id),
        User(username="fritz", password=generate_password_hash("passwort"), photo_url="https://example.com/photo.jpg", location="St. Gallen", skills="Kotlin,Android", latitude=47.4245, longitude=9.3767, team_id=team1.id),
        User(username="gregor", password=generate_password_hash("abc123"), photo_url="https://example.com/photo.jpg", location="Genf", skills="Go,Rust", latitude=46.2044, longitude=6.1432, team_id=team1.id),
        User(username="hannah", password=generate_password_hash("hallo456"), photo_url="https://example.com/photo.jpg", location="Lausanne", skills="Swift,iOS", latitude=46.5197, longitude=6.6323, team_id=team2.id),
        User(username="ivan", password=generate_password_hash("filip"), photo_url="https://example.com/photo.jpg", location="Biel", skills="HTML,CSS", latitude=47.1367, longitude=7.2468, team_id=team2.id),
        User(username="julia", password=generate_password_hash("mypw"), photo_url="https://example.com/photo.jpg", location="Chur", skills="SQL,DBA", latitude=46.8508, longitude=9.5310, team_id=team3.id),
        User(username="kevin", password=generate_password_hash("123456"), photo_url="https://example.com/photo.jpg", location="Zug", skills="PHP,Laravel", latitude=47.1662, longitude=8.5155, team_id=team1.id),
        User(username="lisa", password=generate_password_hash("filip"), photo_url="https://example.com/photo.jpg", location="Thun", skills="Ruby,Rails", latitude=46.7570, longitude=7.6270, team_id=team2.id),
        User(username="marco", password=generate_password_hash("devpass"), photo_url="https://example.com/photo.jpg", location="Aarau", skills="C++,Qt", latitude=47.3906, longitude=8.0451, team_id=team1.id),
        User(username="nina", password=generate_password_hash("filip"), photo_url="https://example.com/photo.jpg", location="Uster", skills="Design,UX", latitude=47.3471, longitude=8.7202, team_id=team2.id),
        User(username="oliver", password=generate_password_hash("testtest"), photo_url="https://example.com/photo.jpg", location="Schaffhausen", skills="Angular,TypeScript", latitude=47.6964, longitude=8.6356, team_id=team1.id),
        User(username="paula", password=generate_password_hash("pass987"), photo_url="https://example.com/photo.jpg", location="Fribourg", skills="NoSQL,Big Data", latitude=46.8065, longitude=7.1619, team_id=team3.id),
        User(username="quentin", password=generate_password_hash("filip"), photo_url="https://example.com/photo.jpg", location="Neuchâtel", skills="Machine Learning", latitude=46.9896, longitude=6.9293, team_id=team3.id),
        User(username="rachel", password=generate_password_hash("zxcvb"), photo_url="https://example.com/photo.jpg", location="Baden", skills="Docker,Kubernetes", latitude=47.4744, longitude=8.3063, team_id=team3.id),
        User(username="stephan", password=generate_password_hash("geheim"), photo_url="https://example.com/photo.jpg", location="Liestal", skills="DevOps,CICD", latitude=47.4867, longitude=7.7345, team_id=team1.id),
        User(username="tanja", password=generate_password_hash("filip"), photo_url="https://example.com/photo.jpg", location="Wetzikon", skills="Testing,Jest", latitude=47.3266, longitude=8.7941, team_id=team2.id)
    ])
    db.session.commit()

    print("✅ Datenbank mit 3 Teams und 20 Benutzern initialisiert.")
