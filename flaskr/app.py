import redis
from flask_cors import CORS
from flaskr import servers
from flaskr import chat
from flaskr import auth
from flask_socketio import SocketIO
from flaskr.models import db
import os
import flaskr.call
from flask_session import Session
from flask import Flask
import eventlet
eventlet.monkey_patch(thread=True)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="my_secret_key",
        SQLALCHEMY_DATABASE_URI='postgres://postgres:password@localhost:5400/Conference',
        SESSION_TYPE='redis',
        SESSION_REDIS=redis.from_url('redis://localhost:6379'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.register_blueprint(auth.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(servers.bp)
    db.init_app(app)

    Session(app)

    chat.socketio.init_app(app, manage_session=False, async_mode="eventlet",
                           cors_allowed_origins="*")
    auth.login_manager.init_app(app)
    CORS(app, supports_credentials=True)

    return app
