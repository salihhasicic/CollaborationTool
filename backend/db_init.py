from app import app
from extensions import db
from models import User, Team
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    team1 = Team(name="Dev Team")
    db.session.add(team1)
    db.session.commit()

    user1 = User(
        username="alice",
        password=generate_password_hash("1234"),
        photo_url="https://example.com/photo1.jpg",
        location="Zürich",
        skills="Python,Flask",
        team_id=team1.id
    )

    user2 = User(
        username="bob",
        password=generate_password_hash("5678"),
        photo_url="https://example.com/photo2.jpg",
        location="Bern",
        skills="JavaScript,Vue"
    )

    db.session.add_all([user1, user2])
    db.session.commit()
    print("✅ Datenbank initialisiert mit Dummy-Daten.")
