from flask import Blueprint, request, jsonify
from models import Message
from extensions import db
from utils import get_gpt_reply


chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/send', methods=['POST'])
def send_message():
    data = request.json
    msg = Message(sender_id=data['sender_id'], team_id=data['team_id'], content=data['content'])
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message': 'Message sent'})

@chat_bp.route('/team/<int:team_id>', methods=['GET'])
def get_team_messages(team_id):
    messages = Message.query.filter_by(team_id=team_id).order_by(Message.timestamp).all()
    result = [{
        'sender_id': m.sender_id,
        'content': m.content,
        'timestamp': m.timestamp.isoformat()
    } for m in messages]
    return jsonify(result)

@chat_bp.route('/suggest', methods=['POST'])
def suggest_reply():
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Kein Nachrichtentext angegeben."}), 400

    suggested = get_gpt_reply(user_message)
    return jsonify({"suggested_reply": suggested})
