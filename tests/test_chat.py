import pytest
from tests.test_fixture import client, app
from flask_socketio import test_client
from tests.test_auth import register_login
from tests.test_room import create_room, get_rooms
import json


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


def test_get_messages__multiple_messages(client):
    register_login(client, "jghf", "hbvnv")
    create_room(client, "hfgfg", "")
    create_message(client, "hfgfg")
    res = get_messages(client, "hfgfg")
    assert json.loads(res.data) == [['gdf']]


def test_get_messages__wrong_room(client):
    register_login(client, "hg", "hfh")
    res = get_messages(client,  "")
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_messages__unauthorized(client):
    res = get_messages(client, "")
    assert res.status_code == 401


def test_create_message__correct(client):
    ds = 2
