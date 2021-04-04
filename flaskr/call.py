from .servers import socketio, user_join_room, get_users_in_room
from flask_socketio import join_room, emit
from .worker import connect
from flask import request, jsonify
from flask import session
from flask_login import current_user
import json


@socketio.on("join_call")
def join_call(data):
    room = data['room'] + "-call"
    user_join_room(current_user, request.sid, room)
    user_array = get_users_in_room(room)
    emit("users_in_call", user_array)


@socketio.on("send_signal")
def send_signal_to_user(data):
    signal_data = {"sending_user": request.sid,
                   "signal": data['signal'], "user": current_user.username}
    emit('user_joined', signal_data, room=data['user'])


@socketio.on('return_signal')
def send_return_signal(data):
    return_user_data = {"signal": data['signal'], "user": request.sid}
    emit('returning_signal', return_user_data, room=data['user'])


@socketio.on('left_call')
def left_call(data):
    room = data['room'] + "-call"
    emit("leave_room", {"room": room})
    users_array = get_users_in_room(room)
    for users in users_array:
        emit("user_left_call", {"user": request.sid},
             room=users['sid'])


@socketio.on('add_track')
def add_track(data):
    print(data)
    emit('added_track', {"user": request.sid})


@socketio.on('remove_track')
def remove_track():
    emit('removed_track', {"user": request.sid})
