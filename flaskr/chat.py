from flask_socketio import join_room, send, emit, SocketIO
from flask import session
from flask_login import current_user
socketio = SocketIO()


@socketio.on('join')
def on_join(data):
    print(current_user)
    # username = data['username']
    # room = data['room']
    # join_room(room)
    # send(username + ' has entered the room.', room=room)
