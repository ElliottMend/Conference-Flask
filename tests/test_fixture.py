import os
import tempfile
import pytest
from flaskr.models import db
from flask.testing import FlaskClient
from flaskr.app import create_app
from flask_socketio import SocketIOTestClient
from flaskr.chat import socketio


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
