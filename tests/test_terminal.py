import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.terminal import convert_notebook


class TestTerminal:
    def test_convert_notebook_not_found(self):
        success, msg = convert_notebook('nonexistent.npy')
        assert success is False
        assert msg == 'File not found'

    def test_convert_invalid_json(self):
        with tempfile.NamedTemporaryFile(suffix='.npy', mode='w', delete=False) as f:
            f.write('not json')
            tmp = f.name
        try:
            success, msg = convert_notebook(tmp)
            assert success is False
            assert msg == 'Invalid JSON'
        finally:
            os.remove(tmp)

    def test_convert_valid_notebook(self):
        cells = [
            {'language': 'python', 'code': 'print("hello")'},
            {'language': 'html', 'code': '<h1>Title</h1>'},
            {'language': 'markdown', 'code': '# Readme'}
        ]
        with tempfile.NamedTemporaryFile(suffix='.npy', mode='w', delete=False) as f:
            json.dump({'cells': cells}, f)
            tmp = f.name
        try:
            success, msg = convert_notebook(tmp)
            assert success is True
            output_dir = msg
            assert os.path.isdir(output_dir)
            assert os.path.isfile(os.path.join(output_dir, 'main.py'))
            assert os.path.isfile(os.path.join(output_dir, 'cell_1.html'))
            assert os.path.isfile(os.path.join(output_dir, 'cell_2.md'))
            # Cleanup
            import shutil
            shutil.rmtree(output_dir)
        finally:
            os.remove(tmp)
