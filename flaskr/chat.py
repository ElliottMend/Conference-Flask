from flask import session, request, Blueprint, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from flask_socketio import emit, rooms
from flaskr.room import socketio, check_user_access
from flaskr.models import User, Room, UserRoom, Message, db
import json
import redis
bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/getmessages', methods=['get'])
@login_required
def get_messages():
    data = json.loads(request.data)
    room = check_user_access(data['room'])
    messages = db.session.query(Message.datetime, Message.message, User.username)\
        .join(UserRoom, Message.user_room_id == UserRoom.id)\
        .join(Room, Room.id == UserRoom.room_id)\
        .join(User, User.id == UserRoom.user_id)\
        .filter(Room.room_name == data['room']).all()
    arr = []
    for i in messages:
        res = {
            "timestamp": i[0],
            "message": i[1],
            "user": i[2]
        }
        arr.append(res)
    return jsonify(arr)


def getTime():
    return datetime.now().strftime('%H:%M:%S')


@socketio.on('message')
def handle_message(data):
    user_room_id = UserRoom.query.filter_by(
        room_id=session['room']).first()
    return_data = {"user": current_user.username,
                   "message": data['message'], "timestamp": getTime()}
    add_message = Message(user_room_id=user_room_id.id,
                          message=data['message'])
    db.session.add(add_message)
    db.session.commit()
    emit('message sent', return_data, room=session['room'])
