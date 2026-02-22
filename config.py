import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
WORKSPACE_DIR = os.path.join(BASE_DIR, 'workspace') # For File Explorer
DB_PATH = os.path.join(DATA_DIR, 'nbook.db')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nbook-secret-key'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WORKSPACE = WORKSPACE_DIR
    NBOOK_MODE = 'free'
    NBOOK_API_KEY = None
