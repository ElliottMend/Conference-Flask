import functools
import json
import uuid
import sqlalchemy
import sys
from flask import Blueprint, abort, jsonify, request, session
from flask_login import current_user, login_required
from flask_socketio import (SocketIO, disconnect, emit, join_room, leave_room,
                            rooms, send)
from werkzeug.security import generate_password_hash
from flaskr.models import Inboxs, Messages, Servers, Users, UserServers, db
from flaskr.worker import connect

bp = Blueprint('servers', __name__, url_prefix='/servers')

socketio = SocketIO()


def check_user_access(data):
    query = db.session.query(Servers.server_name, Servers.id)\
        .join(UserServers, UserServers.server_id == Servers.id)\
        .filter(Servers.server_name == data)\
        .filter(UserServers.user_id == current_user.id).first()
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


def user_join_room(user, sid, server):
    join_room(server)
    data = json.dumps(
        {'user_id': user.id, "username": user.username, "sid": sid})
    connect.hset('server_users', server, data)


def get_users_in_server(server):
    users = db.session.query(Users.id)\
        .join(UserServers, UserServers.user_id == Users.id)\
        .filter(UserServers.server_id == server).all()
    return users


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


@ bp.route('/create_server', methods=['POST'])
@ login_required
def create_server():
    data = json.loads(request.data)
    server_name = data['server']
    if server_name == "":
        return "Invalid server name", 400
    password = None
    if "password" in data:
        password = data['password']
    server_id = str(uuid.uuid4())
    new_server = Servers(
        id=server_id, server_name=server_name, server_password=generate_password_hash(password))
    new_user_server = UserServers(server_id=server_id, user_id=current_user.id)
    db.session.add(new_server)
    db.session.commit()
    db.session.add(new_user_server)
    db.session.commit()
    socketio.emit('new server')
    return "Server created", 200


@ bp.route('/invite_user', methods=['POST'])
@ login_required
def invite_to_server():
    data = json.loads(request.data)
    check_user_access(data['server'])
    query = db.session.query(Users.id)\
        .filter(Users.id == data['user']).first()
    if not query:
        return "User does not exist", 403
    new = Inboxs(sent_user=current_user.id,
                 received_user=data['user'], server_id=data['server'])
    db.session.add(new)
    db.session.commit()
    data = {"user": session_id, "server": data['server']}
    emit('new_inbox', data)
    session_id = json.loads(connect.hget(
        'active_users', data['user']))['session_id']
    socketio.emit('invited_user_server', data)
    leave_room(session_id)
    return 'User was successfully invited', 200


@ bp.route('/join_server', methods=['POST'])
@ login_required
def join_new_server():
    data = json.loads(request.data)
    new_user_server = UserServers(
        server_id=data['server'], user_id=current_user.id)
    socketio.emit("new server")
    return "You have joined the server", 200


@ bp.route('/get_servers', methods=['GET'])
@ login_required
def get_servers():
    query = db.session.query(Servers)\
        .join(UserServers, UserServers.user_id == current_user.id)\
        .filter(Servers.id == UserServers.server_id).all()
    server = []
    for i in query:
        data = {"server_id": i.id, "server_name": i.server_name}
        server.append(data)
    return jsonify(server)


@ socketio.on('connect')
@ connected_users_hook('connect')
def user_connect():
    pass


@ socketio.on('disconnect')
@ connected_users_hook('disconnect')
def user_disconnect():
    pass


@socketio.on('new_server')
def new_server_created(data):
    get_servers()


@socketio.on('new_inbox')
def new_inbox(data):
    join_room(session_id)
    pass


@ socketio.on('join_room')
@ authenticated_only
def on_join(data):
    server = check_user_access(data['server'])
    session['server'] = server[1]
    user_join_room(current_user, request.sid, server[1])
    users = get_users_in_server(server[1])
    arr = []
    for i, v in enumerate(users):
        user = json.loads(connect.hget('active_users', v[i]))
        arr.append(user['username'])
    emit('connected', arr)


@socketio.on('leave_server')
def leave_server():
    pass
