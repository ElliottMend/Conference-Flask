from flask import session, request, Blueprint, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from flask_socketio import rooms, emit
from flaskr.servers import socketio, check_user_access
from flaskr.models import Users, Servers, UserServers, Messages, db
import json
import redis
bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/get_messages', methods=['get'])
@login_required
def get_messages():
    data = json.loads(request.data)
    server = check_user_access(data['server'])
    messages = db.session.query(Messages.datetime, Messages.message, Users.username)\
        .join(UserServers, Messages.user_server_id == UserServers.id)\
        .join(Servers, Servers.id == UserServers.server_id)\
        .join(Users, Users.id == UserServers.user_id)\
        .filter(Servers.server_name == data['server']).all()
    arr = []
    for i in messages:
        res = {
            "timestamp": i[0],
            "message": i[1],
            "user": i[2]
        }
        arr.append(res)
    return jsonify(arr)


def getTime():
    return datetime.now().strftime('%H:%M:%S')


@socketio.on('send_message')
def handle_message(data):
    user_server_id = UserServers.query.filter_by(
        server_id=session['server']).first()
    return_data = {"user": current_user.username,
                   "message": data['message'], "timestamp": getTime()}
    add_message = Messages(user_server_id=user_server_id.id,
                           message=data['message'])
    db.session.add(add_message)
    db.session.commit()
    emit('message_sent', return_data, rooms=session['server'])
