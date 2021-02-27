from app import create_app
from flaskr import chat
app = create_app()

if __name__ == "__main__":
    chat.socketio.run(app)
