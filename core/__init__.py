from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Initialize Extensions here
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# Import models
from core.models import Notebook
