from flask_socketio import join_room, send, emit, SocketIO
from flask import session, request, Blueprint, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from flaskr.models import User, Room, UserRoom, Message, db
from werkzeug.security import generate_password_hash
import json
import uuid
bp = Blueprint('chat', __name__, url_prefix='/chat')


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
    messages = Message.query\
        .join(
            UserRoom, Message.user_room_id == UserRoom.id)\
        .join(Room, Room.id == UserRoom.room_id)\
        .join(User, User.id == UserRoom.user_id)\
        .filter(Room.room_name == data['room']).all()
    return jsonify(messages)


def getTime():
    return datetime.now().strftime('%H:%M:%S')


def getDate():
    return datetime.now().strftime('%d-%m-%Y')


socketio = SocketIO()


@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        room = Room.query.\
            join(UserRoom, Room.id == UserRoom.room_id).\
            filter(UserRoom.user_id == current_user.id).\
            filter(Room.room_name == data['room']).\
            first()
        session['room'] = room
        join_room(room)
    else:
        return "Not logged in", 404


@socketio.on('message')
def handle_message(message):
    print('fds')
    # user_room_id =
    # add_message = Message(user_room_id=user_room_id, message=message)
    # send(
    #     {
    #         'user': current_user.screen_name,
    #         'message': message,
    #         'timestamp': getTime()
    #     }, room=session['room'])
