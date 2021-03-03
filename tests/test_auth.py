import pytest
from tests.test_fixture import client, app, auth_client
import json


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


def test_register__no_username(client):
    res = register(client, "", "password", "email")
    assert res.status_code == 400


def test_register__no_password(client):
    res = register(client, "username", "", "email")
    assert res.status_code == 400


def test_register__no_email(client):
    res = res = register(client, "username", "password", "")
    assert res.status_code == 400


def test_register__correct(client):
    register_user = register(
        client, "username", "pass", "email@email.com"
    )
    assert register_user.status_code == 200


def test_register__incorrect_email_format(client):
    register_user = register(
        client, "fds", "pass", "emailemailcom"
    )
    assert register_user.status_code == 400


def test_register__user_already_authenticated(auth_client):
    register_page = register(auth_client, "fhfgh", "gfdg", "gfdf")
    assert register_page.status_code == 403


def test_login__correct(client):
    login_user = register_login(
        client, "mghfm", "abcde"
    )
    assert login_user.status_code == 200


def test_login__password_does_not_match(client):
    register_user = register(
        client, "dsffds", "p", "email@email.com"
    )
    login_user = login(
        client, "dsffds", "pass"
    )
    assert login_user.status_code == 401


def test_login__username_does_not_match(client):
    register_user = register(
        client, "hgff", "pass", "email@email.com"
    )
    login_user = login(
        client, "22222", "fds@fsdf.com"
    )
    assert login_user.status_code == 404


def test_login__email_used_for_username(client):
    login_user = register_login(
        client, "email@email.com", "mnn"
    )
    assert login_user.status_code == 200


def test_login__user_already_authenticated(auth_client):
    login_page = login(auth_client, "fhfgh", "gfdg")
    assert login_page.status_code == 403


def test_logout__user_not_authenticated(client):
    res = client.get('/auth/logout')
    assert res.status_code == 401


def test_logout__correct(auth_client):
    res = auth_client.get('/auth/logout')
    assert res.status_code == 200
