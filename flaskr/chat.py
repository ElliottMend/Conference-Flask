from flask_socketio import join_room, send, emit, SocketIO
from flask import session, request, Blueprint, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from flaskr import models
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
    if "password" in data is not None:
        password = data['password']
    room_id = str(uuid.uuid4())
    new_room = models.Room(
        id=room_id, room_name=room_name, room_password=password)
    new_user_room = models.UserRoom(room_id=room_id, user_id=current_user.id)
    models.db.session.add(new_room)
    models.db.session.add(new_user_room)
    models.db.session.commit()
    return "room created", 200


@bp.route('/getrooms', methods=['GET'])
@login_required
def get_rooms():
    user_id = current_user.id
    user_room = models.UserRoom.query.filter_by(user_id=user_id).all()
    array = []
    for i in user_room:
        rooms = models.db.session.query(
            models.Room.room_name).filter(models.Room.id == i.room_id).all()
        array.append(rooms[0])
    return jsonify(array)


@bp.route('/getmessages', methods=['get'])
@login_required
def get_messages():
    data = json.loads(request.data)
    messages = models.Message.query\
        .join(
            models.UserRoom, models.Message.user_room_id == models.UserRoom.id)\
        .join(models.Room, models.Room.id == models.UserRoom.room_id)\
        .join(models.User, models.User.id == models.UserRoom.user_id)\
        .filter(models.Room.room_name == data['room']).all()
    print(messages)
    return data


def getTime():
    return datetime.now().strftime('%H:%M:%S')


def getDate():
    return datetime.now().strftime('%d-%m-%Y')


socketio = SocketIO()


@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        room = models.Room.query.\
            join(models.UserRoom, models.Room.id == models.UserRoom.room_id).\
            filter(models.UserRoom.user_id == current_user.id).\
            filter(models.Room.room_name == data['room']).\
            first()
        session['room'] = room
        join_room(room)
    else:
        return "Not logged in", 404


@socketio.on('message')
def handle_message(message):
    print('fds')
    # user_room_id =
    # add_message = models.Message(user_room_id=user_room_id, message=message)
    # send(
    #     {
    #         'user': current_user.screen_name,
    #         'message': message,
    #         'timestamp': getTime()
    #     }, room=session['room'])
