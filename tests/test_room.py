import pytest
from tests.test_fixture import client, app, auth_client
from flask_socketio import SocketIOTestClient
from tests.test_auth import register_login
from flaskr.chat import socketio
import json


def create_room(client, room, password):
    return client.post('/chat/create', data=json.dumps(dict(
        room=room,
        password=password
    )))


def get_rooms(client):
    return client.get('/chat/getrooms')


def connect_socket(user_client):
    return SocketIOTestClient(user_client, socketio)


def test_create_room__unauthorized(client):
    res = client.post('/chat/create', data=json.dumps(dict(
        room="gfd",
        password="hfh"
    )))
    assert res.status_code == 401


def test_create_room__correct(auth_client):
    res = create_room(auth_client, "room_name", "")
    assert res.data == b"room created"


def test_create_room__password_correct(auth_client):
    res = create_room(auth_client, "room", "password")
    assert res.data == b"room created"


def test_create_room__incorrect(auth_client):
    res = create_room(auth_client, "", "")
    assert res.status_code == 400


def test_get_rooms__correct(auth_client):
    res = get_rooms(auth_client)
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_rooms__multiple_rooms(auth_client):
    create_room(auth_client, "fds", "")
    create_room(auth_client, "fs", "")
    create_room(auth_client, "f", "")
    create_room(auth_client, "ds", "")
    res = auth_client.get('/chat/getrooms')
    assert json.loads(res.data) == [['fds'], ['fs'], ['f'], ['ds']]
    assert len(json.loads(res.data)) == 4


def test_get_rooms_unauthorized(client):
    res = client.get('/chat/getrooms')
    assert res.status_code == 401


def test_connect():
    socketio_client = connect_socket(app)
    assert socketio_client.is_connected()


def test_disconnect():
    socketio_client = connect_socket(app)
    socketio_client.disconnect()
    assert socketio_client.is_connected() == False


def test_client_sid():
    socketio_client1 = connect_socket(app)
    socketio_client2 = connect_socket(app)
    assert socketio_client1.eio_sid != socketio_client2.eio_sid


def test_join_room__unauthorized():
    socketio_client = connect_socket(app)
    assert socketio_client.is_connected()
    socketio_client.emit('join', {'room': "dgd"})
    assert socketio_client.is_connected() == False


def test_join_room__name(auth_client):
    create_room(auth_client, "abc", "")
    socketio_client = SocketIOTestClient(
        app, socketio, flask_test_client=auth_client)
    assert socketio_client.is_connected()
    socketio_client.emit('join', {'room': 'abc'})
    received = socketio_client.get_received()
    assert len(received) == 1
    assert received[0]['args'][0] == {'room': 'abc'}


def test_join_room__name_unauthorized(client):
    register_login(client, 'fhf', 'hfh')
    socketio_client = SocketIOTestClient(
        app, socketio, flask_test_client=client)
    assert socketio_client.is_connected()
    socketio_client.emit('join', {'room': 'fds'})
    assert socketio_client.is_connected() == False
