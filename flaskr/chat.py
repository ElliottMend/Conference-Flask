from flask_socketio import join_room, send, emit, SocketIO, disconnect
from flask import session, request, Blueprint, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from flaskr.models import User, Room, UserRoom, Message, db
from werkzeug.security import generate_password_hash
import json
import functools
import sqlalchemy
import uuid
bp = Blueprint('chat', __name__, url_prefix='/chat')


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        print('dsa')
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@bp.route('/create', methods=['POST'])
@login_required
def create_room():
    data = json.loads(request.data)
    room_name = data['room']
    if room_name == "":
        return "invalid room name", 400
    password = None
    if "password" in data:
        password = data['password']
    room_id = str(uuid.uuid4())
    new_room = Room(
        id=room_id, room_name=room_name, room_password=generate_password_hash(password))
    new_user_room = UserRoom(room_id=room_id, user_id=current_user.id)
    db.session.add(new_room)
    db.session.add(new_user_room)
    db.session.commit()
    return "room created", 200


@bp.route('/getrooms', methods=['GET'])
@login_required
def get_rooms():
    query = db.session.query(Room.room_name)\
        .join(UserRoom, UserRoom.user_id == current_user.id)\
        .filter(Room.id == UserRoom.room_id).all()
    return jsonify(query)


@bp.route('/getmessages', methods=['get'])
@login_required
def get_messages():
    data = json.loads(request.data)
    messages = db.session.query(Message.datetime, Message.message, User.screen_name)\
        .join(
            UserRoom, Message.user_room_id == UserRoom.id)\
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


def getDate():
    return datetime.now().strftime('%d-%m-%Y')


socketio = SocketIO()

socketio.on('connect')


def on_connect():
    emit('connect', {'message': 'User connected'})


@socketio.on('disconnect')
def on_disconnect():
    emit('disconnect', {"message": "You were disconnected"})


@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        room = Room.query.\
            join(UserRoom, Room.id == UserRoom.room_id).\
            filter(UserRoom.user_id == current_user.id).\
            filter(Room.room_name == data['room']).\
            first()
        if not room:
            emit('disconnect', {
                "message": "You are not in a room with this name"})
            disconnect()
        else:
            session['room'] = room.id
            join_room(room.id)
            emit('connected', data)
    else:
        return disconnect()


@socketio.on('message')
def handle_message(data):
    user_room_id = UserRoom.query.filter_by(
        room_id=session['room']).first()
    return_data = {"user": current_user.screen_name,
                   "message": data['message'], "timestamp": getTime()}
    add_message = Message(user_room_id=user_room_id.id,
                          message=data['message'])
    db.session.add(add_message)
    db.session.commit()
    emit('message sent', return_data, room=session['room'])
