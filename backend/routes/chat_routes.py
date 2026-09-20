from flask import Blueprint, jsonify, g, abort
from models import Message, User
from extensions import db
from security import data, text, integer, team_access, utc_iso
from utils import get_gpt_reply, AIUnavailable

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
def send_message():
    body = data()
    if 'sender_id' in body and integer(body['sender_id']) != g.user.id:
        abort(403, description='Du kannst nur in deinem eigenen Namen schreiben.')
    team = team_access(integer(body.get('team_id')))
    message = Message(sender_id=g.user.id, team_id=team.id,
                      content=text(body.get('content', ''), 'Nachricht', 10000, True))
    db.session.add(message)
    db.session.commit()
    return jsonify(message='Nachricht gesendet.', id=message.id)

@chat_bp.route('/team/<int:team_id>')
def get_team_messages(team_id):
    team_access(team_id)
    messages = Message.query.filter_by(team_id=team_id).order_by(Message.timestamp, Message.id).all()
    names = {u.id: u.username for u in User.query.all()}
    return jsonify([{'id': m.id, 'sender_id': m.sender_id, 'sender_name': names.get(m.sender_id, str(m.sender_id)),
                     'content': m.content, 'timestamp': utc_iso(m.timestamp)} for m in messages])

@chat_bp.route('/suggest', methods=['POST'])
def suggest_reply():
    message = text(data().get('message', ''), 'Nachricht', 10000, True)
    try:
        return jsonify(suggested_reply=get_gpt_reply(message))
    except AIUnavailable as error:
        return jsonify(message=str(error), error=str(error)), 503
