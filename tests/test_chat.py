import pytest
from conftest import client, app, auth_client, auth_socketio_client
from flask_socketio import SocketIOTestClient
from tests.test_room import create_room, get_rooms
from flaskr.room import socketio, check_user_access
import json
from datetime import datetime
from werkzeug import exceptions


def get_messages(client, room):
    return client.get('/chat/getmessages', data=json.dumps(dict(
        room=room
    )))


def test_check_user_access__correct(auth_client):
    create_room(auth_client, "fsd", "")
    res = check_user_access("fsd")
    assert res[0] == 'fsd'


def test_get_messages__correct(auth_client):
    create_room(auth_client, "fsd", "")
    res = get_messages(auth_client, "fsd")
    assert res.status_code == 200
    assert len(json.loads(res.data)) == 0
    assert json.loads(res.data) == []


def test_get_messages__wrong_room(auth_client):
    assert get_messages(auth_client,  "gdf").status_code == 401


def test_get_messages__unauthorized(client):
    res = get_messages(client, "")
    assert res.status_code == 401


def test_create_message__correct(auth_socketio_client):
    auth_socketio_client.emit('join', {"room": "room"})
    auth_socketio_client.get_received()
    auth_socketio_client.emit('message', {"message": "gfdg"})
    time = datetime.now().strftime('%H:%M:%S')
    received = auth_socketio_client.get_received()
    assert len(received[0]['args'][0]) == 3
    assert received[0]['args'][0] == {
        "user": "username", "message": "gfdg", "timestamp": time}


def test_create_message__(auth_socketio_client):
    auth_socketio_client.emit('join', {"room": "room"})
    auth_socketio_client.get_received()
    auth_socketio_client.emit('message', {'message': 'dfds'})
    received = auth_socketio_client.get_received()
    assert len(received) > 0


def test_get_messages__multiple_messages(auth_client, auth_socketio_client):
    auth_socketio_client.emit('join', {"room": "room"})
    auth_socketio_client.get_received()
    time = datetime.utcnow().strftime('%a, %d %B %Y %H:%M:%S GMT')
    auth_socketio_client.emit('message', {"message": "gfdg"})
    auth_socketio_client.emit('message', {"message": "gfdg"})
    res = get_messages(auth_client, "room")
    assert len(json.loads(res.data)) == 2
    assert json.loads(res.data) == [
        {'message': 'gfdg',
         'timestamp': json.loads(res.data)[0]['timestamp'],
         'user': 'username'},
        {'message': 'gfdg',
         'timestamp': json.loads(res.data)[1]['timestamp'],
         'user': 'username'}, ]
