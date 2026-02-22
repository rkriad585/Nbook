from flask import Flask
from config import Config

# Import Core Components
from core import db, socketio
from core.routes import main_bp
from core.cli import create_cli

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    socketio.init_app(app)

    # Register Routes
    app.register_blueprint(main_bp)

    return app

# Create the application instance
app = create_app()

# Create the CLI
cli = create_cli(app)

if __name__ == '__main__':
    cli()
