from flask import Blueprint, jsonify, g, abort
from sqlalchemy import or_, and_
from extensions import db
from models import User, PrivateMessage
from security import data, text, integer, utc_iso

private_chat_bp = Blueprint('private_chat', __name__)

@private_chat_bp.route('/chat/private/send', methods=['POST'])
def send_private_message():
    body = data()
    if 'sender_id' in body and integer(body['sender_id']) != g.user.id:
        abort(403, description='Du kannst nur in deinem eigenen Namen schreiben.')
    receiver = db.get_or_404(User, integer(body.get('receiver_id')))
    content = text(body.get('content', ''), 'Nachricht', 10000, True)
    message = PrivateMessage(sender_id=g.user.id, receiver_id=receiver.id, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify(message='Nachricht gesendet.', id=message.id)

@private_chat_bp.route('/chat/private/<int:user1_id>/<int:user2_id>')
def get_private_messages(user1_id, user2_id):
    if g.user.id not in (user1_id, user2_id):
        abort(403, description='Dieses Gespräch gehört nicht zu deinem Konto.')
    db.get_or_404(User, user1_id)
    db.get_or_404(User, user2_id)
    messages = PrivateMessage.query.filter(or_(
        and_(PrivateMessage.sender_id == user1_id, PrivateMessage.receiver_id == user2_id),
        and_(PrivateMessage.sender_id == user2_id, PrivateMessage.receiver_id == user1_id)
    )).order_by(PrivateMessage.timestamp, PrivateMessage.id).all()
    names = {u.id: u.username for u in User.query.filter(User.id.in_([user1_id, user2_id]))}
    return jsonify([{'id': m.id, 'sender_id': m.sender_id, 'receiver_id': m.receiver_id,
                     'sender_name': names.get(m.sender_id, str(m.sender_id)),
                     'receiver_name': names.get(m.receiver_id, str(m.receiver_id)),
                     'content': m.content, 'timestamp': utc_iso(m.timestamp)} for m in messages])

@private_chat_bp.route('/chat/private/conversations')
def conversations():
    rows = PrivateMessage.query.filter(or_(PrivateMessage.sender_id == g.user.id,
                                          PrivateMessage.receiver_id == g.user.id)).order_by(PrivateMessage.timestamp.desc(), PrivateMessage.id.desc())
    latest = {}
    for row in rows:
        partner = row.receiver_id if row.sender_id == g.user.id else row.sender_id
        if partner not in latest:
            latest[partner] = {'partner_id': partner, 'sender_id': row.sender_id,
                               'content': row.content, 'timestamp': utc_iso(row.timestamp)}
    return jsonify(list(latest.values()))
