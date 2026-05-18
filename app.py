from flask import Flask, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

# Import Core Components
from core import db, socketio
from core.routes import main_bp
from core.cli import create_cli

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute", "20 per second"])

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    socketio.init_app(app)
    limiter.init_app(app)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://cdn.tailwindcss.com https://code.jquery.com 'unsafe-inline' 'unsafe-eval'; style-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com 'unsafe-inline'; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' ws: wss:"
        return response

    # Register Routes
    app.register_blueprint(main_bp)

    return app

# Create the application instance
app = create_app()

# Create the CLI
cli = create_cli(app)

if __name__ == '__main__':
    cli()
