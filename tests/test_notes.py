import pytest
from flask_socketio import SocketIOTestClient
from tests.test_auth import register_login
from flaskr.chat import socketio
import json
