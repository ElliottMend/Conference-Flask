import pytest
from conftest import client, app, auth_client
from flask_socketio import SocketIOTestClient
from tests.test_auth import register_login
from flaskr.chat import socketio
from flaskr.servers import check_user_access
import json
from unittest.mock import MagicMock
from werkzeug import exceptions


def create_server(client, server, password):
    return client.post('/server/create_server', data=json.dumps(dict(
        server=server,
        password=password
    )))


def get_servers(client):
    return client.get('/server/get_servers')


def join_server(client, server, password):
    return client.post('/server/join_server', data=json.dumps(dict(
        server=server,
        password=password
    )))


def test_check_user_access__correct(auth_client):
    create_server(auth_client, "fsd", "")
    res = check_user_access("fsd")
    assert res[0] == 'fsd'


def invite_user(client, user, server):
    return client.post('/server/invite_user', data=json.dumps(dict(
        server=server,
        user=user
    )))


def connect_socket(app, user_client):
    return SocketIOTestClient(app, socketio, flask_test_client=user_client)


def test_create_server__unauthorized(client):
    res = client.post('/server/create_server', data=json.dumps(dict(
        server="gfd",
        password="hfh"
    )))
    assert res.status_code == 401


def test_create_server__correct(auth_client):
    res = create_server(auth_client, "server_name", "")
    assert res.status_code == 200
    assert res.data == b"Server created"


def test_create_server__password_correct(auth_client):
    res = create_server(auth_client, "server", "password")
    assert res.status_code == 200
    assert res.data == b"Server created"


def test_create_server__incorrect(auth_client):
    res = create_server(auth_client, "", "")
    assert res.status_code == 400
    assert res.data == b'Invalid server name'


def test_invite_server__correct(client_no_context, auth_client):
    register_login(client_no_context, "fdsf", "fdsvcxvfsd")
    create_server(auth_client, "server", "")
    res = invite_user(auth_client, "1", "server")
    assert res.status_code == 200
    assert res.data == b'User was successfully invited'


def test_invite_server__incorrect_user(auth_client):
    create_server(auth_client, "dsa", "vxcv")
    res = invite_user(auth_client, "", "dsa")
    assert res.status_code == 403
    assert res.data == b'User does not exist'


def test_invite_server__incorrect_server(auth_client):
    create_server(auth_client, "dwa", "dsa")
    res = invite_user(auth_client, "abc", "")
    assert res.status_code == 401
    assert res.data == b'Not Authorized'


def test_invite_server__unauthorized(client):
    res = invite_user(client, "user", "server")
    assert res.status_code == 401


def test_join_server__correct(auth_client):
    res = join_server(auth_client, "server", "password")
    assert res.status_code == 200


def test_join_server__incorrect(auth_client):
    res = join_server(auth_client, "", "cbcb")
    assert res.status_code == 403
    assert res.data == b"Incorrect password"


def test_join_server__unauthorized(client):
    res = join_server(client, "server", "password")
    assert res.status == "401 UNAUTHORIZED"


def test_get_servers__correct(auth_client):
    res = get_servers(auth_client)
    assert res.status_code == 200
    assert json.loads(res.data) == []
    assert len(json.loads(res.data)) == 0


def test_get_servers__multiple_servers(auth_client):
    create_server(auth_client, "fds", "")
    create_server(auth_client, "fs", "")
    res = auth_client.get('/server/get_servers')
    assert res.status_code == 200
    assert len(json.loads(res.data)) == 2


def test_get_servers_unauthorized(client):
    res = client.get('/server/get_servers')
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


def test_connect_to_server__unauthorized(auth_socketio_client):
    with pytest.raises(exceptions.Unauthorized):
        assert auth_socketio_client.is_connected()
        auth_socketio_client.emit('join_room', {'server': "rfdf"})
        assert auth_socketio_client.is_connected() == False


def test_connect_to_server__name_correct(auth_socketio_client):
    auth_socketio_client.emit('join_room', {'server': 'server'})
    received = auth_socketio_client.get_received()
    assert len(received) == 1
    assert received[0]['args'][0] == ['username']


def test_connect_to_server__name_unauthorized(auth_socketio_client):
    with pytest.raises(exceptions.Unauthorized):
        assert auth_socketio_client.is_connected()
        auth_socketio_client.emit('join_room', {'server': 'fds'})
        assert auth_socketio_client.is_connected() == False
