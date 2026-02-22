from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Initialize Extensions here
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# Define Models here to be accessible everywhere
class Notebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
