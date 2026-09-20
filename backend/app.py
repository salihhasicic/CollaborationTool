import os
from flask import Flask, request, jsonify, g
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from extensions import db

app = Flask(__name__, instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'))
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///collab.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={'connect_args': {'timeout': 30}},
    JWT_TOKEN_LOCATION=['headers'],
    MAX_CONTENT_LENGTH=20 * 1024 * 1024,
)
db.init_app(app)
from security import persistent_secret
app.config['JWT_SECRET_KEY'] = persistent_secret(app.instance_path, 'jwt-secret', 'JWT_SECRET_KEY')
jwt = JWTManager(app)
from models import User, RevokedToken

@jwt.token_in_blocklist_loader
def revoked(header, payload):
    return db.session.get(RevokedToken, payload['jti']) is not None

@jwt.invalid_token_loader
def invalid(reason):
    return jsonify(message='Bitte erneut einloggen.'), 401

@jwt.expired_token_loader
def expired(header, payload):
    return jsonify(message='Deine Sitzung ist abgelaufen. Bitte erneut einloggen.'), 401

@app.before_request
def authenticate():
    if request.endpoint is None or request.method == 'OPTIONS':
        return
    if request.endpoint in ('auth.login', 'auth.register', 'team.get_all_teams'):
        if request.endpoint == 'team.get_all_teams':
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            g.user = db.session.get(User, int(identity)) if identity else None
        return
    verify_jwt_in_request()
    try:
        g.user = db.session.get(User, int(get_jwt_identity()))
    except (TypeError, ValueError):
        g.user = None
    if g.user is None:
        return jsonify(message='Bitte erneut einloggen.'), 401

@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(message=error.description, error=error.description), error.code

@app.errorhandler(IntegrityError)
def conflict(error):
    db.session.rollback()
    return jsonify(message='Diese Änderung steht im Konflikt mit vorhandenen Daten.'), 409

from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.team_routes import team_bp
from routes.chat_routes import chat_bp
from routes.project_routes import project_bp
from routes.private_chat_routes import private_chat_bp
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(team_bp, url_prefix='/team')
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(project_bp)
app.register_blueprint(private_chat_bp)
from migrations import migrate
migrate(app)

if __name__ == '__main__':
    app.run(port=int(os.environ.get('BACKEND_PORT', '5001')), debug=True)
