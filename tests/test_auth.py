import pytest
from conftest import client, app, auth_client
from flaskr.auth import handle_data
import json
import werkzeug


def register(client, username, password, email):
    return client.post('/auth/register', data=json.dumps(dict(
        username=username,
        password=password,
        email=email
    )), follow_redirects=True)


def login(client, username, password):
    return client.post('/auth/login', data=json.dumps(dict(
        username=username,
        password=password
    )), follow_redirects=True)


def register_login(client, username, password):
    if "@" in username:
        register(
            client, "gddfgd", password, username
        )
    else:
        register(
            client, username, password, "gddf@dgdf.com"
        )
    return login(client, username, password)


def test_handle_data__correct():
    res = handle_data(json.dumps(dict(
        username='user',
        password='pass'
    )))
    assert res == ('user', 'pass')


def test_handle_data__with_email():
    res = handle_data(json.dumps(dict(
        username='user',
        password='pass',
        email='e@e.com'
    )))
    assert res == ('user', 'pass', 'e@e.com')


def test_handle_data__no_username():
    with pytest.raises(ValueError):
        user = handle_data(json.dumps(dict(
            username='',
            password='pass',
            email='e@e.com'
        )))


def test_handle_data__no_password():
    with pytest.raises(ValueError):
        handle_data(json.dumps(dict(
            username='user',
            password='',
            email='e@e.com'
        )))


def test_handle_data__wrong_email_format():
    with pytest.raises(ValueError):
        handle_data(json.dumps(dict(
            username='user',
            password='pass',
            email='ee.com'
        )))


def test_register__correct(client):
    res = register(
        client, "username", "pass", "email@email.com"
    )
    assert res.data == b"You have successfully registered"
    assert res.status_code == 200


def test_register__user_already_authenticated(auth_client):
    res = register(auth_client, "fhfgh", "gfdg", "gfdf")
    assert res.data == b'User is already logged in'
    assert res.status_code == 401


def test_login__correct(client):
    res = register_login(
        client, "mghfm", "abcde"
    )
    assert res.data == b"logged in"
    assert res.status_code == 200


def test_login__password_does_not_match(client):
    register_user = register(
        client, "dsffds", "p", "email@email.com"
    )
    res = login(
        client, "dsffds", "pass"
    )
    assert res.data == b'Password is incorrect'
    assert res.status_code == 400


def test_login__username_does_not_match(client):
    register_user = register(
        client, "hgff", "pass", "email@email.com"
    )
    res = login(
        client, "22222", "fds@fsdf.com"
    )
    assert res.data == b'The Username or Email is incorrect'
    assert res.status_code == 400


def test_login__email_used_for_username(client):
    res = register_login(
        client, "email@email.com", "mnn"
    )
    assert res.data == b'logged in'
    assert res.status_code == 200


def test_login__user_already_authenticated(auth_client):
    res = login(auth_client, "fhfgh", "gfdg")
    assert res.data == b'User is already logged in'
    assert res.status_code == 401


def test_logout__user_not_authenticated(client):
    res = client.get('/auth/logout')
    assert res.status_code == 401


def test_logout__correct(auth_client):
    res = auth_client.get('/auth/logout')
    assert res.status_code == 200
    assert res.data == b'logged out'
