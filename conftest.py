import os
import tempfile
import pytest
from flaskr.models import db, User
from flask.testing import FlaskClient
from flaskr.app import create_app
from flask_socketio import SocketIOTestClient
from flaskr.chat import socketio
import json
from flask_socketio import SocketIOTestClient
from flaskr.chat import socketio
from werkzeug.security import generate_password_hash


class SQLAlchemyTest():
    def set_up_db():
        db.create_all()

    def load_data():
        db.create_all()
        user = User(username="username", password=generate_password_hash("password"),
                    email="email@email.com")
        db.session.add(user)
        db.session.commit()

    def delete_db():
        db.session.remove()
        db.drop_all()


app = create_app()


@pytest.fixture
def client():
    app.app_context().push()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            SQLAlchemyTest.set_up_db()
            yield client
    SQLAlchemyTest.delete_db()


@pytest.fixture
def auth_client(client):
    SQLAlchemyTest.load_data()
    client.post('/auth/login', data=json.dumps(dict(
        username='username',
        password='password'
    )))
    yield client


@pytest.fixture
def auth_socketio_client(auth_client):
    auth_client.post('/room/create', data=json.dumps(dict(
        room='room',
        password=''
    )))
    so = SocketIOTestClient(
        app, socketio, flask_test_client=auth_client)
    yield so
    print('disconnect')
    if so.is_connected():
        so.disconnect()
