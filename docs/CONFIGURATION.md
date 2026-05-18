# Nbook Configuration

Nbook uses `config.py` for application configuration, with support for environment variables via `python-dotenv`.

## config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WORKSPACE_DIR = os.path.join(BASE_DIR, 'workspace')
DB_PATH = os.path.join(DATA_DIR, 'nbook.db')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nbook-secret-key')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WORKSPACE = WORKSPACE_DIR
    NBOOK_MODE = os.environ.get('NBOOK_MODE', 'free')
    NBOOK_API_KEY = None
    NBOOK_PORT = int(os.environ.get('NBOOK_PORT', 52896))
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
```

## Configuration Reference

### Directory Paths

| Setting | Default | Description |
|---------|---------|-------------|
| `BASE_DIR` | `app root` | Absolute path to the application root |
| `DATA_DIR` | `{BASE_DIR}/data` | Stores the SQLite database file |
| `WORKSPACE_DIR` | `{BASE_DIR}/workspace` | Root for file explorer and git clones |
| `DB_PATH` | `{DATA_DIR}/nbook.db` | Full path to the SQLite database |

Both `data/` and `workspace/` directories are created automatically on startup.

### Flask Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `SECRET_KEY` | `nbook-secret-key` | Used for session signing. **Override in production!** |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///{DB_PATH}` | Database connection string |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Disables object tracking (saves memory) |
| `MAX_CONTENT_LENGTH` | `52,428,800` (50MB) | Maximum file upload size |
| `SESSION_COOKIE_SAMESITE` | `Lax` | CSRF protection for session cookies |
| `SESSION_COOKIE_HTTPONLY` | `True` | Prevents JS access to session cookies |

### Nbook Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `NBOOK_MODE` | `free` | Operation mode: `free` or `secure` |
| `NBOOK_API_KEY` | `None` | API key for secure mode (auto-generated) |
| `NBOOK_PORT` | `52896` | Server port (configurable via env) |

### Workspace

| Setting | Default | Description |
|---------|---------|-------------|
| `WORKSPACE` | `{BASE_DIR}/workspace` | Root directory for all file operations |

## Environment Variables

Create a `.env` file in the project root:

```env
# Flask secret key (REQUIRED for production)
SECRET_KEY=your-strong-random-secret-here

# Server port (default: 52896)
NBOOK_PORT=52896

# Operation mode (free or secure)
NBOOK_MODE=free
```

Nbook loads `.env` automatically via `python-dotenv`. A template is provided at `.env.example`.

## Database

Nbook uses SQLite by default (`data/nbook.db`). The schema is auto-created on startup via `db.create_all()`. The database contains two tables: `user` and `notebook`.

To reset the database (development only):
```bash
# Delete the database file
rm data/nbook.db   # Linux/macOS
del data\nbook.db  # Windows

# Restart the server (tables recreated automatically)
python app.py free
```

## Changing the Port

```bash
# Via environment variable
export NBOOK_PORT=8080   # Linux/macOS
$env:NBOOK_PORT=8080    # PowerShell
set NBOOK_PORT=8080     # Windows CMD

# Via .env file
echo "NBOOK_PORT=8080" >> .env
```

## Using a Different Database

While Nbook defaults to SQLite, you can use any SQLAlchemy-supported database:

```python
# config.py (example for PostgreSQL)
import os
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:pass@localhost/nbook'
)
```

## Production Deployment

For production:

1. **Set a strong SECRET_KEY** — Use a random generator:
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Use secure mode** — Run with API key protection:
   ```bash
   python app.py start
   ```

3. **Use a production WSGI server** — Gunicorn (Linux) or Waitress (Windows):
   ```bash
   pip install gunicorn  # Linux
   gunicorn -w 4 'app:create_app()' -b 0.0.0.0:52896
   
   pip install waitress  # Windows
   waitress-serve --port=52896 'app:create_app()'
   ```

4. **Use Redis for rate limiting** — Flask-Limiter shows a warning about in-memory storage; configure Redis for multi-process deployments.

5. **Configure HTTPS** — Use a reverse proxy (Nginx, Caddy) for TLS termination.
