import os
import tempfile
import pytest
from flaskr.models import db
from flask.testing import FlaskClient
from flaskr.app import create_app


class SQLAlchemyTest():
    def set_up_db():
        db.create_all()

    def delete_db():
        db.session.remove()
        db.drop_all()


app = create_app()


@pytest.fixture
def client():
    app.app_context().push()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/testing.db'
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            SQLAlchemyTest.set_up_db()
            yield client
    SQLAlchemyTest.delete_db()


def socketio():
    flask_test_client = app.test_client()

    socketio_test_client = socketio.test_client(
        app, flask_test_client=flask_test_client)

    assert not socketio_test_client.is_connected()

    r = flask_test_client.post('/login', data={
        'username': 'python', 'password': 'is-great!'})
    assert r.status_code == 200

    socketio_test_client = socketio.test_client(
        app, flask_test_client=flask_test_client)

    r = socketio_test_client.get_received()
    assert len(r) == 1
    assert r[0]['name'] == 'welcome'
    assert len(r[0]['args']) == 1
    assert r[0]['args'][0] == {'username': 'python'}


socketio_test()
