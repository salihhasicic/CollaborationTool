from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime
from models import User

private_chat_bp = Blueprint('private_chat', __name__)

PRIVATE_CHAT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'private_messages.json')

def load_private_messages():
    if os.path.exists(PRIVATE_CHAT_FILE):
        with open(PRIVATE_CHAT_FILE, "r") as f:
            return json.load(f)
    return []

def save_private_messages(msgs):
    with open(PRIVATE_CHAT_FILE, "w") as f:
        json.dump(msgs, f)

@private_chat_bp.route('/chat/private/send', methods=['POST'])
def send_private_message():
    data = request.json
    sender_id = int(data['sender_id'])
    receiver_id = int(data['receiver_id'])
    content = data['content']
    timestamp = datetime.utcnow().isoformat()
    # Username auflösen
    sender = User.query.get(sender_id)
    receiver = User.query.get(receiver_id)
    sender_name = sender.username if sender else str(sender_id)
    receiver_name = receiver.username if receiver else str(receiver_id)
    msgs = load_private_messages()
    msgs.append({
        "sender_id": sender_id,
        "sender_name": sender_name,
        "receiver_id": receiver_id,
        "receiver_name": receiver_name,
        "content": content,
        "timestamp": timestamp
    })
    save_private_messages(msgs)
    return jsonify({"message": "Nachricht gesendet."})

@private_chat_bp.route('/chat/private/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_private_messages(user1_id, user2_id):
    msgs = load_private_messages()
    # Zeige alle Nachrichten zwischen user1 und user2 (beide Richtungen)
    filtered = [
        m for m in msgs
        if (m['sender_id'] == user1_id and m['receiver_id'] == user2_id)
        or (m['sender_id'] == user2_id and m['receiver_id'] == user1_id)
    ]
    # Optional: sortiere nach Zeit
    filtered.sort(key=lambda m: m['timestamp'])
    return jsonify(filtered)
