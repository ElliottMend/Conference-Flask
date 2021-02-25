from app import app
from flask_session import Session
from models import db
from flask_socketio import SocketIO
import chat
from flask_cors import CORS
from flask_login import LoginManager
import auth
app.config['SECRET_KEY'] = 'my_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
chat.socketio.init_app(app, manage_session=False,
                       async_mode='eventlet', cors_allowed_origins="*")
Session(app)
auth.login_manager.init_app(app)
db.init_app(app)
CORS(app)

if __name__ == "__main__":
    app.register_blueprint(auth.bp)
    chat.socketio.run(app)
