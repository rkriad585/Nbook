# Nbook Configuration

Nbook's configuration is managed through the `config.py` file, which defines essential settings for the Flask application, database, workspace, and operational modes.

## `config.py`

```python
import os

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Directory for application data (e.g., database)
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Directory for user workspace (file explorer, cloned repos)
WORKSPACE_DIR = os.path.join(BASE_DIR, 'workspace')

# Path to the SQLite database file
DB_PATH = os.path.join(DATA_DIR, 'nbook.db')

# Ensure data and workspace directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class Config:
    """
    Main configuration class for the Flask application.
    """
    # Flask Secret Key: Used for session management and security.
    # It's highly recommended to set this via an environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nbook-secret-key'

    # SQLAlchemy Database URI: Specifies the database connection string.
    # Nbook uses SQLite for simplicity.
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'

    # SQLALCHEMY_TRACK_MODIFICATIONS: Disables tracking object modifications
    # to save memory, as it's not needed for Nbook's current use case.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # WORKSPACE: Path to the directory where user files and projects are stored.
    WORKSPACE = WORKSPACE_DIR

    # NBOOK_MODE: Defines the operational mode of Nbook ('free' or 'secure').
    # This is set dynamically by the CLI commands.
    NBOOK_MODE = 'free'

    # NBOOK_API_KEY: Stores the API key when Nbook is running in 'secure' mode.
    # This is generated at runtime.
    NBOOK_API_KEY = None
```

## Key Configuration Parameters

### 1. Directory Paths

*   **`BASE_DIR`**: The absolute path to the directory where `config.py` resides. This serves as the root for other relative paths.
*   **`DATA_DIR`**: A subdirectory within `BASE_DIR` (e.g., `Nbook/data`) used to store application-specific data, primarily the SQLite database.
    *   Automatically created if it doesn't exist (`os.makedirs(DATA_DIR, exist_ok=True)`).
*   **`WORKSPACE_DIR`**: A subdirectory within `BASE_DIR` (e.g., `Nbook/workspace`) designated as the root for the file explorer and where Git repositories are cloned.
    *   Automatically created if it doesn't exist (`os.makedirs(WORKSPACE_DIR, exist_ok=True)`).
*   **`DB_PATH`**: The full path to the SQLite database file (`nbook.db`) located inside `DATA_DIR`.

### 2. Flask Application Settings (`Config` class)

*   **`SECRET_KEY`**:
    *   **Purpose**: Essential for cryptographic operations in Flask, such as signing session cookies.
    *   **Value**: Defaults to `'nbook-secret-key'` if the `SECRET_KEY` environment variable is not set.
    *   **Recommendation**: For any deployment beyond local development, it is crucial to set this to a strong, randomly generated value via an environment variable (e.g., `export SECRET_KEY='your_very_secret_key_here'`) to prevent security vulnerabilities.
*   **`SQLALCHEMY_DATABASE_URI`**:
    *   **Purpose**: Configures the database connection for Flask-SQLAlchemy.
    *   **Value**: `sqlite:///{DB_PATH}` points to the SQLite database file.
    *   **Customization**: While Nbook currently uses SQLite, this setting could be modified to connect to other databases (e.g., PostgreSQL, MySQL) if the necessary drivers and schema migrations were implemented.
*   **`SQLALCHEMY_TRACK_MODIFICATIONS`**:
    *   **Purpose**: Controls whether Flask-SQLAlchemy tracks modifications of objects and emits signals.
    *   **Value**: Set to `False` to conserve resources, as Nbook does not rely on these signals.
*   **`WORKSPACE`**:
    *   **Purpose**: Specifies the root directory for all file system operations exposed through the Nbook interface.
    *   **Value**: Set to `WORKSPACE_DIR`.
*   **`NBOOK_MODE`**:
    *   **Purpose**: Determines the operational security mode of the Nbook instance.
    *   **Value**: Can be `'free'` or `'secure'`. It is initially `'free'` but is dynamically updated by the CLI commands (`python app.py start` sets it to `'secure'`, `python app.py free` sets it to `'free'`).
*   **`NBOOK_API_KEY`**:
    *   **Purpose**: Stores the unique API key generated when Nbook runs in `secure` mode.
    *   **Value**: `None` by default. When `python app.py start` is executed, a UUID is generated and assigned here. This key is then required for all authenticated access.

## Environment Variables

While `SECRET_KEY` is the only configuration explicitly checking for an environment variable, it's a best practice to manage sensitive or deployment-specific settings outside of the codebase.

To set the `SECRET_KEY` environment variable (e.g., on Linux/macOS):
```bash
export SECRET_KEY="your_long_and_random_secret_key_here"
python app.py start # or free
```
On Windows (Command Prompt):
```cmd
set SECRET_KEY="your_long_and_random_secret_key_here"
python app.py start
```
On Windows (PowerShell):
```powershell
$env:SECRET_KEY="your_long_and_random_secret_key_here"
python app.py start
```

Understanding and managing these configuration parameters is crucial for deploying and customizing your Nbook instance effectively.

written by Neorwc