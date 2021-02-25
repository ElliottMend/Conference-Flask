from flask_socketio import join_room, send, emit, SocketIO
from flask import session, request, Blueprint
from flask_login import current_user, login_required
socketio = SocketIO()


@socketio.on('join')
def on_join(data):
    room = data['room']
    session['room'] = room
    join_room(room)
    send({'user': current_user.screen_name,
          'message': ' has entered the room.'}, room=room)


@socketio.on('message')
def handle_message(message):
    send({'user': current_user.screen_name,
          'message': message}, room=session['room'])
