import pytest
from tests.test_fixture import client, app
from tests.test_auth import register_login
import json


def create_room(client, room, password):
    register_login(client, "fdsf", "gdfg")
    res = client.post('/chat/create', data=json.dumps(dict(
        room=room,
        password=password
    )))
    return res


def get_rooms(client):
    register_login(client, "fdsf", "gdfg")
    res = client.get('/chat/getrooms')
    return res


def test_create_room__unauthorized(client):
    res = client.post('/chat/create', data=json.dumps(dict(
        room="gfd",
        password="hfh"
    )))
    assert res.status_code == 401


def test_create_room__correct(client):
    res = create_room(client, "room_name", "")
    assert res.data == b"room created"


def test_create_room__password_correct(client):
    res = create_room(client, "room", "password")
    assert res.data == b"room created"


def test_create_room__incorrect(client):
    res = create_room(client, "", "")
    assert res.status_code == 400


def test_get_rooms_correct(client):
    res = get_rooms(client)
    assert res.status_code == 200


def test_get_rooms_unauthorized(client):
    res = client.get('/chat/getrooms')
    assert res.status_code == 401
