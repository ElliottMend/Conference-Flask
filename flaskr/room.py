from flask import Blueprint, request, session, jsonify, abort
from flask_socketio import join_room, send, emit, SocketIO, rooms, disconnect
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_required
from flaskr.models import User, Room, UserRoom, Message, db, Inbox
import functools
import sqlalchemy
import json
import uuid

bp = Blueprint('room', __name__, url_prefix='/room')

socketio = SocketIO()

active_users = {'active': []}


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
                active_users['active'].append(
                    {'username': current_user.screen_name, 'session': sessionid})
            elif action == 'disconnect':
                for idx, user in enumerate(active_users['active']):
                    if user['session'] == sessionid:
                        active_users['active'].pop(idx)
                        break
            return f(*args, **kwargs)
        return wrapped
    return real_connected_users_hook


@socketio.on('connect')
@connected_users_hook('connect')
def user_connect():
    pass


@socketio.on('disconnect')
@connected_users_hook('disconnect')
def user_disconnect():
    pass


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


@bp.route('/invite')
@login_required
def invite_to_room(data):
    check_user_access()
    new = Inbox(user_id=)


@bp.route('/join_room', methods=['POST'])
@login_required
def join_new_room(data):

    return 'room'


@bp.route('/getrooms', methods=['GET'])
@login_required
def get_rooms():
    query = db.session.query(Room.room_name)\
        .join(UserRoom, UserRoom.user_id == current_user.id)\
        .filter(Room.id == UserRoom.room_id).all()
    return jsonify(query)


@socketio.on('join')
@authenticated_only
def on_join(data):
    room = check_user_access(data['room'])
    session['room'] = room[1]
    join_room(room[1])
    emit('connected', active_users)
