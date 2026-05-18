import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app import create_app


class TestRoutes:
    @pytest.fixture(autouse=True)
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['NBOOK_MODE'] = 'free'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            from core import db
            db.drop_all()
            db.create_all()
        return app

    def test_home_page(self, app):
        with app.test_client() as client:
            r = client.get('/')
            assert r.status_code == 200
            assert b'N-BOOK' in r.data

    def test_system_stats(self, app):
        with app.test_client() as client:
            r = client.get('/system/stats')
            assert r.status_code == 200
            json_data = r.get_json()
            assert 'status' in json_data
            assert json_data['status'] == 'online'

    def test_variables_empty(self, app):
        with app.test_client() as client:
            r = client.get('/variables')
            assert r.status_code == 200
            assert r.get_json() == []

    def test_file_list(self, app):
        with app.test_client() as client:
            r = client.get('/files/list')
            assert r.status_code == 200

    def test_history_page(self, app):
        with app.test_client() as client:
            r = client.get('/history')
            assert r.status_code == 200

    def test_404(self, app):
        with app.test_client() as client:
            r = client.get('/nonexistent')
            assert r.status_code == 404

    def test_kernel_restart(self, app):
        with app.test_client() as client:
            r = client.post('/kernel/restart')
            assert r.status_code == 200
            assert r.get_json()['status'] == 'restarted'

    def test_kernel_cancel(self, app):
        with app.test_client() as client:
            r = client.post('/kernel/cancel')
            assert r.status_code == 200
            assert r.get_json()['status'] == 'cancelled'

    def test_save_and_load_notebook(self, app):
        with app.test_client() as client:
            save_r = client.post('/save', json={
                'title': 'Test Notebook',
                'cells': [{'code': 'print("hi")', 'language': 'python'}]
            })
            assert save_r.status_code == 200
            nb_id = save_r.get_json()['id']
            load_r = client.get(f'/history/load/{nb_id}')
            assert load_r.status_code == 200
            data = load_r.get_json()
            assert data['title'] == 'Test Notebook'
            assert len(data['cells']) == 1

    def test_save_file_and_read(self, app):
        with app.test_client() as client:
            with app.app_context():
                ws = app.config['WORKSPACE']
                os.makedirs(ws, exist_ok=True)
            save_r = client.post('/save-file', json={
                'path': 'test_route.txt',
                'content': 'hello route'
            })
            assert save_r.status_code == 200
            read_r = client.get('/files/read?path=test_route.txt')
            assert read_r.status_code == 200
            assert read_r.get_json()['content'] == 'hello route'
            os.remove(os.path.join(ws, 'test_route.txt'))

    def test_create_and_delete_file(self, app):
        with app.test_client() as client:
            with app.app_context():
                ws = app.config['WORKSPACE']
                os.makedirs(ws, exist_ok=True)
            create_r = client.post('/files/create', json={
                'path': 'test_del.txt',
                'type': 'file'
            })
            assert create_r.status_code == 200
            del_r = client.post('/files/delete', json={'path': 'test_del.txt'})
            assert del_r.status_code == 200

    def test_secure_mode_blocks(self, app):
        app.config['NBOOK_MODE'] = 'secure'
        app.config['NBOOK_API_KEY'] = 'test-key'
        with app.test_client() as client:
            r = client.get('/files/list')
            assert r.status_code == 403

    def test_secure_mode_with_key(self, app):
        app.config['NBOOK_MODE'] = 'secure'
        app.config['NBOOK_API_KEY'] = 'test-key'
        with app.test_client() as client:
            r = client.get('/files/list?key=test-key')
            assert r.status_code == 200
