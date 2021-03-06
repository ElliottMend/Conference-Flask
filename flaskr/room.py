from flask import Blueprint, request, session, jsonify, abort
from flask_socketio import join_room, send, emit, leave_room, SocketIO, rooms, disconnect
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
from flaskr.models import User, Room, UserRoom, Message, db, Inbox
import functools
from flaskr.worker import connect
import sqlalchemy
import json
import uuid

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
                data = json.dumps({'username': current_user.screen_name,
                                   'session_id': sessionid})
                connect.hset('active_users', current_user.id, data)
            elif action == 'disconnect':
                connect.hdel('active_users', sessionid)
            return f(*args, **kwargs)
        return wrapped
    return real_connected_users_hook


@ socketio.on('connect')
@ connected_users_hook('connect')
def user_connect():
    pass


@ socketio.on('disconnect')
@ connected_users_hook('disconnect')
def user_disconnect():
    pass


@ bp.route('/create', methods=['POST'])
@ login_required
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
    socketio.emit('new room')
    return "room created", 200


@ bp.route('/invite_user', methods=['POST'])
@ login_required
def invite_to_room():
    data = json.loads(request.data)
    check_user_access(data['room'])
    query = db.session.query(User.id)\
        .filter(User.id == data['user'])
    if not query:
        return "User does not exist", 403
    new = Inbox(sent_user=current_user.id,
                received_user=data['user'], room_id=data['room'])
    db.session.add(new)
    db.session.commit()
    session_id = json.loads(connect.hget(
        'active_users', data['user']))['session_id']
    print(session_id)
    join_room(session_id)
    socketio.emit('invite sent', room=session_id)
    leave_room(session_id)
    return 'User was successfully invited'


@ bp.route('/join_room', methods=['POST'])
@ login_required
def join_new_room(data):
    return 'room'


@ bp.route('/getrooms', methods=['GET'])
@ login_required
def get_rooms():
    query = db.session.query(Room.room_name)\
        .join(UserRoom, UserRoom.user_id == current_user.id)\
        .filter(Room.id == UserRoom.room_id).all()
    return jsonify(query)


@socketio.on('new room')
def new_room_created(data):
    get_rooms()


@ socketio.on('join')
@ authenticated_only
def on_join(data):
    room = check_user_access(data['room'])
    session['room'] = room[1]
    join_room(room[1])
    emit('connected', json.loads(connect.hget('active_users', current_user.id)))
