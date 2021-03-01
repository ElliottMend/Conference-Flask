import pytest
from tests.test_fixture import client, app
from tests.test_auth import register_login
import json


def create_room(client, room, password):
    return client.post('/chat/create', data=json.dumps(dict(
        room=room,
        password=password
    )))


def get_rooms(client):
    return client.get('/chat/getrooms')


def test_create_room__unauthorized(client):
    res = client.post('/chat/create', data=json.dumps(dict(
        room="gfd",
        password="hfh"
    )))
    assert res.status_code == 401


def test_create_room__correct(client):
    register_login(client, "fdsf", "gdfg")
    res = create_room(client, "room_name", "")
    assert res.data == b"room created"


def test_create_room__password_correct(client):
    register_login(client, "fdsf", "gdfg")
    res = create_room(client, "room", "password")
    assert res.data == b"room created"


def test_create_room__incorrect(client):
    register_login(client, "fdsf", "gdfg")
    res = create_room(client, "", "")
    assert res.status_code == 400


def test_get_rooms__correct(client):
    register_login(client, "fdsf", "gdfg")
    res = get_rooms(client)
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_rooms__multiple_rooms(client):
    register_login(client, "fdsf", "gdfg")
    create_room(client, "fds", "")
    create_room(client, "fs", "")
    create_room(client, "f", "")
    create_room(client, "ds", "")
    res = client.get('/chat/getrooms')
    assert json.loads(res.data) == [['fds'], ['fs'], ['f'], ['ds']]
    assert len(json.loads(res.data)) == 4


def test_get_rooms_unauthorized(client):
    res = client.get('/chat/getrooms')
    assert res.status_code == 401
