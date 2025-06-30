from flask import Flask
from flask_cors import CORS
from extensions import db  # <-- NEU test

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collab.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app)

# Blueprint-Importe nach Initialisierung
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.team_routes import team_bp
from routes.chat_routes import chat_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(team_bp, url_prefix='/team')
app.register_blueprint(chat_bp, url_prefix='/chat')

if __name__ == '__main__':
    app.run(debug=True)
