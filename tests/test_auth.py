import pytest
from tests.test_fixture import client, app
import json


def register(client, username, password, email):
    return client.post('/auth/register', data=json.dumps(dict(
        username=username,
        password=password,
        email=email
    )), follow_redirects=True)


def login(client, username, password, email):
    return client.post('/auth/login', data=json.dumps(dict(
        username=username,
        password=password
    )), follow_redirects=True)


def test_register_login(client):
    register_user = register(
        client, "username", "password", "email@email.com")
    login_user = login(
        client, "username", "password", "email@email.com"
    )
    assert register_user.status_code == 200 and login_user.status_code == 200
