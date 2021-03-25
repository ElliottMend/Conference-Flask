import functools
import json
import uuid
import sqlalchemy
from flask import Blueprint, abort, jsonify, request, session
from flask_login import current_user, login_required
from flask_socketio import (SocketIO, disconnect, emit, join_room, leave_room,
                            rooms, send)
from werkzeug.security import generate_password_hash
from flaskr.models import Inbox, Message, Room, User, UserRoom, db
from flaskr.worker import connect

bp = Blueprint('room', __name__, url_prefix='/room')

socketio = SocketIO()


def check_user_access(data):
    query = db.session.query(Room.room_name, Room.id)\
        .join(UserRoom, UserRoom.room_id == Room.id)\
        .filter(Room.room_name == data)\
        .filter(UserRoom.user_id == current_user.id).first()
    if not query:
        abort(401, description="Not authorized")
    else:
        return query


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


def connected_users_hook(action):
    def real_connected_users_hook(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            sessionid = request.sid
            if action == 'connect':
                data = json.dumps({'username': current_user.username,
                                   'session_id': sessionid})
                connect.hset('active_users', current_user.id, data)
            elif action == 'disconnect':
                connect.hdel('active_users', sessionid)
            return f(*args, **kwargs)
        return wrapped
    return real_connected_users_hook


@ bp.route('/create', methods=['POST'])
@ login_required
def create_room():
    data = json.loads(request.data)
    room_name = data['room']
    if room_name == "":
        return "Invalid room name", 400
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
    socketio.emit('new room')
    return "Room created", 200


@ bp.route('/invite_user', methods=['POST'])
@ login_required
def invite_to_room():
    data = json.loads(request.data)
    check_user_access(data['room'])
    query = db.session.query(User.id)\
        .filter(User.id == data['user']).first()
    if not query:
        return "User does not exist", 403
    new = Inbox(sent_user=current_user.id,
                received_user=data['user'], room_id=data['room'])
    db.session.add(new)
    db.session.commit()
    session_id = json.loads(connect.hget(
        'active_users', data['user']))['session_id']
    join_room(session_id)
    socketio.emit('invited', room=session_id)
    leave_room(session_id)
    return 'User was successfully invited', 200


@ bp.route('/join_room', methods=['POST'])
@ login_required
def join_new_room(data):
    new_user_room = UserRoom(room_id=data['room'], user_id=current_user.id)
    socketio.emit("new room")
    return "Joined room", 200


@ bp.route('/getrooms', methods=['GET'])
@ login_required
def get_rooms():
    query = db.session.query(Room.room_name)\
        .join(UserRoom, UserRoom.user_id == current_user.id)\
        .filter(Room.id == UserRoom.room_id).all()
    return jsonify(query)


@ socketio.on('connect')
@ connected_users_hook('connect')
def user_connect():
    pass


@ socketio.on('disconnect')
@ connected_users_hook('disconnect')
def user_disconnect():
    pass


@socketio.on('new room')
def new_room_created(data):
    get_rooms()


@ socketio.on('join')
@ authenticated_only
def on_join(data):
    room = check_user_access(data['room'])
    session['room'] = room[1]
    join_room(room[1])
    users = db.session.query(User.id)\
        .join(UserRoom, UserRoom.user_id == User.id)\
        .filter(UserRoom.room_id == room[1]).all()
    arr = []
    for i, v in enumerate(users):
        user = json.loads(connect.hget('active_users', v[i]))
        arr.append(user['username'])
    emit('connected', arr)
