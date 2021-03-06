import pytest
from conftest import client, app, auth_client
from flask_socketio import SocketIOTestClient
from tests.test_auth import register_login
from flaskr.chat import socketio
import json
from unittest.mock import MagicMock
from werkzeug import exceptions


def create_room(client, room, password):
    return client.post('/room/create', data=json.dumps(dict(
        room=room,
        password=password
    )))


def get_rooms(client):
    return client.get('/room/getrooms')


def join_room(client, room, password):
    return client.post('/room/join_room', data=json.dumps(dict(
        room=room,
        password=password
    )))


def invite_user(client, user, room):
    return client.post('/room/invite_user', data=json.dumps(dict(
        room=room,
        user=user
    )))


def connect_socket(app, user_client):
    return SocketIOTestClient(app, socketio, flask_test_client=user_client)


def test_create_room__unauthorized(client):
    res = client.post('/room/create', data=json.dumps(dict(
        room="gfd",
        password="hfh"
    )))
    assert res.status_code == 401


def test_create_room__correct(auth_client):
    res = create_room(auth_client, "room_name", "")
    assert res.status_code == 200
    assert res.data == b"room created"


def test_create_room__password_correct(auth_client):
    res = create_room(auth_client, "room", "password")
    assert res.status_code == 200
    assert res.data == b"room created"


def test_create_room__incorrect(auth_client):
    res = create_room(auth_client, "", "")
    assert res.status_code == 400
    assert res.data == b'invalid room name'


def test_invite_room__correct(client_no_context, auth_client):
    register_login(client_no_context, "fdsf", "fdsvcxvfsd")
    create_room(auth_client, "room", "")
    res = invite_user(auth_client, "1", "room")
    assert res.status_code == 200
    assert res.data == b'User was successfully invited'


def test_invite_room__incorrect_user(auth_client):
    res = invite_user(auth_client, "", "room")
    assert res.status_code == 403
    assert res.data == b'User does not exist'


def test_invite_room__incorrect_room(auth_client):
    res = invite_user(auth_client, "", "room")
    assert res.status_code == 401
    assert res.data == b'Not Authorized'


def test_invite_room__unauthorized(client):
    res = invite_user(client, "user", "room")
    assert res.status_code == 401


def test_join_room__correct(auth_client):
    res = join_room(auth_client, "room", "password")
    assert res.status_code == 200
    assert res.data == b"You have joined the room"


def test_join_room__incorrect(auth_client):
    res = join_room(auth_client, "", "cbcb")
    assert res.status_code == 403
    assert res.data == b"Incorrect password"


def test_join_room__unauthorized(client):
    res = join_room(client, "room", "password")
    assert res.status == 401


def test_get_rooms__correct(auth_client):
    res = get_rooms(auth_client)
    assert res.status_code == 200
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_rooms__multiple_rooms(auth_client):
    create_room(auth_client, "fds", "")
    create_room(auth_client, "fs", "")
    create_room(auth_client, "f", "")
    create_room(auth_client, "ds", "")
    res = auth_client.get('/room/getrooms')
    assert res.status_code == 200
    assert len(json.loads(res.data)) == 4
    assert json.loads(res.data) == [['fds'], ['fs'], ['f'], ['ds']]


def test_get_rooms_unauthorized(client):
    res = client.get('/room/getrooms')
    assert res.status_code == 401


def test_connect(auth_socketio_client):
    assert auth_socketio_client.is_connected()


def test_disconnect(auth_socketio_client):
    auth_socketio_client.disconnect()
    assert auth_socketio_client.is_connected() == False


def test_client_sid(client_no_context):
    register_login(client_no_context, "fdsf", "fdsvcxvfsd")
    socketio_client2 = connect_socket(app, client_no_context)
    register_login(client_no_context, "fdsds", "fdsfsd")
    socketio_client1 = connect_socket(app, client_no_context)
    assert socketio_client1.eio_sid != socketio_client2.eio_sid
    socketio_client1.disconnect()
    socketio_client2.disconnect()


def test_connect_to_room__unauthorized(auth_socketio_client):
    with pytest.raises(exceptions.Unauthorized):
        assert auth_socketio_client.is_connected()
        auth_socketio_client.emit('join', {'room': "rfdf"})
        assert auth_socketio_client.is_connected() == False


def test_connect_to_room__name_correct(auth_socketio_client):
    auth_socketio_client.emit('join', {'room': 'room'})
    received = auth_socketio_client.get_received()
    assert len(received) == 1
    assert received[0]['args'][0] == {'username': 'username', 'user_id': 1}


def test_connect_to_room__name_unauthorized(auth_socketio_client):
    with pytest.raises(exceptions.Unauthorized):
        assert auth_socketio_client.is_connected()
        auth_socketio_client.emit('join', {'room': 'fds'})
        assert auth_socketio_client.is_connected() == False
