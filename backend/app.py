from flask import Flask
from flask_cors import CORS
from extensions import db  # <-- NEU test
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '1234'  # Setze hier einen sicheren Wert!
app.config['JWT_TOKEN_LOCATION'] = ['headers']

db.init_app(app)
CORS(app)
jwt = JWTManager(app)

# Blueprint-Importe nach Initialisierung
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.team_routes import team_bp
from routes.chat_routes import chat_bp
from routes.project_routes import project_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(team_bp, url_prefix='/team')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(project_bp)  # Kein Prefix, damit /projects direkt erreichbar ist

if __name__ == '__main__':
    app.run(debug=True)
