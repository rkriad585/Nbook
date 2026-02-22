import os
import uuid
import json
import shutil
from core import db, socketio

def run_server_secure(app):
    api_key = str(uuid.uuid4())
    app.config['NBOOK_MODE'] = 'secure'
    app.config['NBOOK_API_KEY'] = api_key
    print(f"\n🔒 SECURE MODE: http://127.0.0.1:5000?key={api_key}\n")
    with app.app_context(): db.create_all()
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', use_reloader=False)

def run_server_free(app):
    app.config['NBOOK_MODE'] = 'free'
    print(f"\n🔓 FREE MODE: http://127.0.0.1:5000\n")
    with app.app_context(): db.create_all()
    socketio.run(app, debug=True, port=5000, host='0.0.0.0', use_reloader=False)

def convert_notebook(filename):
    if not os.path.exists(filename): return False, "File not found"
    try:
        with open(filename, 'r') as f: data = json.load(f)
    except: return False, "Invalid JSON"

    base_name = os.path.splitext(filename)[0]
    output_dir = f"{base_name}_project"
    if os.path.exists(output_dir): shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Convert Python Only
    code = "\n\n".join([c['code'] for c in data.get('cells', []) if c['language'] == 'python'])
    with open(f"{output_dir}/main.py", "w") as f: f.write(code)
    
    # Save others as raw text files
    for i, c in enumerate(data.get('cells', [])):
        if c['language'] == 'html':
            with open(f"{output_dir}/cell_{i}.html", "w") as f: f.write(c['code'])
        elif c['language'] == 'markdown':
            with open(f"{output_dir}/cell_{i}.md", "w") as f: f.write(c['code'])
            
    return True, output_dir
