import pytest
from tests.test_fixture import client, app
from flask_socketio import SocketIOTestClient
from tests.test_auth import register_login
from tests.test_room import create_room, get_rooms
from flaskr.chat import socketio
import json
from datetime import datetime


def get_messages(client, room):
    return client.get('/chat/getmessages', data=json.dumps(dict(
        room=room
    )))


def create_message(client, message):
    return client.post


def test_get_messages__correct(client):
    register_login(client, "dsa", "gfd")
    create_room(client, "fsd", "")
    res = get_messages(client, "fsd")
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_messages__wrong_room(client):
    register_login(client, "hg", "hfh")
    res = get_messages(client,  "")
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_messages__unauthorized(client):
    res = get_messages(client, "")
    assert res.status_code == 401


def test_create_message__correct(client):
    register_login(client, "hg", "hfh")
    create_room(client, "ggfd", "")
    socketio_client = SocketIOTestClient(
        app, socketio, flask_test_client=client)
    socketio_client.emit('join', {"room": "ggfd"})
    socketio_client.get_received()
    socketio_client.emit('message', {"message": "gfdg"})
    time = datetime.now().strftime('%H:%M:%S')
    received = socketio_client.get_received()
    assert len(received[0]['args'][0]) == 3
    assert received[0]['args'][0] == {
        "user": "hg", "message": "gfdg", "timestamp": time}


def test_get_messages__multiple_messages(client):
    register_login(client, "hg", "hfh")
    create_room(client, "ggfd", "")
    socketio_client = SocketIOTestClient(
        app, socketio, flask_test_client=client)
    socketio_client.emit('join', {"room": "ggfd"})
    socketio_client.get_received()
    time = datetime.utcnow().strftime('%a, %d %B %Y %H:%M:%S GMT')
    socketio_client.emit('message', {"message": "gfdg"})
    socketio_client.emit('message', {"message": "gfdg"})
    res = get_messages(client, "ggfd")
    assert json.loads(res.data) == [
        {'message': 'gfdg',
         'timestamp': json.loads(res.data)[0]['timestamp'],
         'user': 'hg'},
        {'message': 'gfdg',
         'timestamp': json.loads(res.data)[1]['timestamp'],
         'user': 'hg'}, ]
