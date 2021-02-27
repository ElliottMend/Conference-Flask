from flask import Flask
from flask_session import Session
import os
from flaskr.models import db
from flask_socketio import SocketIO
from flaskr import auth
from flaskr import chat
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="my_secret_key",
        SQLALCHEMY_DATABASE_URI='sqlite:////tmp/test.db',
        SESSION_TYPE='filesystem',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
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
    db.init_app(app)
    Session(app)

    chat.socketio.init_app(app, manage_session=False,
                           async_mode='eventlet', cors_allowed_origins="http://localhost:3000")
    auth.login_manager.init_app(app)
    CORS(app, supports_credentials=True)

    return app
