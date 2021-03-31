from .servers import socketio, user_join_room
from flask_socketio import join_room, emit
from .worker import connect
from flask import request
from flask import session
from flask_login import current_user


@socketio.on("join_call")
def join_call(data):
    server = data['server'] + "-call"
    call_server = join_room(server)
    user_join_room(current_user, request.sid, server)
    # emit("users_in_call", users, room=server)
