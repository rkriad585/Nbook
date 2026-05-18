import os
import json
import mimetypes
import psutil
import sys
import threading
import subprocess
import time
import shutil
from flask import Blueprint, render_template, request, jsonify, abort, current_app, make_response
from flask_socketio import emit
from git import Repo

from core import db, socketio, Notebook
from core.executor import run_python_stateful, get_variables, PYTHON_GLOBALS, cancel_execution

main_bp = Blueprint('main', __name__)

# --- Global Terminal State ---
TERMINAL_FD = None
TERMINAL_PROC = None
try:
    import pty
    HAS_PTY = True
except ImportError:
    HAS_PTY = False

# --- Middleware ---
@main_bp.record_once
def register_middleware(state):
    @state.app.before_request
    def check_api_key():
        if request.path.startswith('/static') or request.path.startswith('/socket.io'): return
        if current_app.config.get('NBOOK_MODE') == 'secure':
            key = request.args.get('key') or request.headers.get('X-API-KEY')
            if key != current_app.config.get('NBOOK_API_KEY'):
                if request.is_json or request.path.startswith('/files') or request.path.startswith('/system'): 
                    abort(403)
                return render_template('error.html'), 403

def get_safe_path(req_path):
    workspace = os.path.abspath(current_app.config['WORKSPACE'])
    target = os.path.abspath(os.path.join(workspace, req_path.strip('/')))
    return target if target.startswith(workspace) else None

# --- Terminal Threads ---
def read_and_emit_pty(fd):
    try:
        while True:
            time.sleep(0.01)
            if fd is not None:
                data = os.read(fd, 1024)
                if not data: break
                socketio.emit('terminal_output', {'output': data.decode(errors='ignore')})
    except OSError: pass
    finally:
        if fd is not None:
            try: os.close(fd)
            except: pass

def read_and_emit_pipe(process):
    try:
        while True:
            if process.poll() is not None: break
            output = process.stdout.read(1024)
            if output:
                socketio.emit('terminal_output', {'output': output.decode(errors='ignore')})
    except: pass
    finally:
        try: process.terminate()
        except: pass

# --- System Stats ---
@main_bp.route('/system/stats')
def system_stats():
    try:
        cpu = 0
        mem_data = {"percent": 0, "used": 0, "total": 0}
        disk_data = {"percent": 0, "used": 0, "total": 0}
        try: cpu = psutil.cpu_percent(interval=None)
        except: pass
        try:
            mem = psutil.virtual_memory()
            mem_data = {"percent": mem.percent, "used": round(mem.used / (1024**3), 2), "total": round(mem.total / (1024**3), 2)}
        except: pass
        try:
            ws = current_app.config.get('WORKSPACE', '.')
            if not os.path.exists(ws): os.makedirs(ws, exist_ok=True)
            disk = psutil.disk_usage(ws)
            disk_data = {"percent": disk.percent, "used": round(disk.used / (1024**3), 2), "total": round(disk.total / (1024**3), 2)}
        except: pass
        return jsonify({"status": "online", "cpu": cpu, "ram": mem_data, "disk": disk_data})
    except Exception as e:
        return jsonify({"status": "online", "error": str(e), "ram": {"percent": 0}, "disk": {"percent": 0}})

# --- File Routes ---
@main_bp.route('/files/list')
def list_files():
    req_path = request.args.get('path', '')
    target_dir = get_safe_path(req_path)
    if not target_dir or not os.path.isdir(target_dir): return jsonify({"error": "Invalid directory"}), 400
    try:
        items = []
        for f in os.listdir(target_dir):
            if f.startswith('.'): continue
            full = os.path.join(target_dir, f)
            items.append({"name": f, "path": os.path.join(req_path, f).replace('\\','/'), "is_dir": os.path.isdir(full)})
        items.sort(key=lambda x: (not x['is_dir'], x['name']))
        return jsonify(items)
    except: return jsonify([])

@main_bp.route('/files/read')
def read_file():
    target = get_safe_path(request.args.get('path', ''))
    if not target or not os.path.isfile(target): return jsonify({"error": "File not found"}), 404
    try:
        mime = mimetypes.guess_type(target)[0]
        is_text_like = mime and ('text' in mime or 'json' in mime or 'xml' in mime or 'svg' in mime)
        if mime and not is_text_like: return jsonify({"error": "Binary file preview not supported"}), 400
        with open(target, 'r', encoding='utf-8', errors='ignore') as f: return jsonify({"content": f.read()})
    except Exception as e: return jsonify({"error": str(e)}), 500

@main_bp.route('/files/delete', methods=['POST'])
def delete_file():
    path = request.json.get('path')
    target = get_safe_path(path)
    if not target: return jsonify({"error": "Invalid path"}), 400
    try:
        if os.path.isdir(target): shutil.rmtree(target)
        else: os.remove(target)
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@main_bp.route('/files/rename', methods=['POST'])
def rename_file():
    old_path = request.json.get('old_path')
    new_name = request.json.get('new_name')
    target_old = get_safe_path(old_path)
    base_dir = os.path.dirname(target_old)
    target_new = os.path.join(base_dir, new_name)
    if not target_old or not os.path.exists(target_old): return jsonify({"error": "File not found"}), 404
    if os.path.exists(target_new): return jsonify({"error": "Name already exists"}), 400
    try:
        os.rename(target_old, target_new)
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"error": str(e)}), 500

@main_bp.route('/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    dest = request.form.get('path', '')
    target_dir = get_safe_path(dest)
    if not target_dir or not os.path.isdir(target_dir):
        return jsonify({"error": "Invalid directory"}), 400
    try:
        filepath = os.path.join(target_dir, file.filename)
        file.save(filepath)
        return jsonify({"status": "success", "path": os.path.join(dest, file.filename).replace('\\', '/')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/files/download')
def download_file():
    target = get_safe_path(request.args.get('path', ''))
    if not target or not os.path.isfile(target):
        return jsonify({"error": "File not found"}), 404
    try:
        with open(target, 'rb') as f:
            data = f.read()
        response = make_response(data)
        response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(target)}'
        response.mimetype = 'application/octet-stream'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/files/create', methods=['POST'])
def create_file():
    path = request.json.get('path', '')
    typ = request.json.get('type', 'file')
    target = get_safe_path(path)
    if not target:
        return jsonify({"error": "Invalid path"}), 400
    try:
        if typ == 'directory':
            os.makedirs(target, exist_ok=True)
        else:
            if os.path.exists(target):
                return jsonify({"error": "Already exists"}), 400
            open(target, 'w').close()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Export Routes ---
@main_bp.route('/export/html', methods=['POST'])
def export_html():
    data = request.json
    cells = data.get('cells', [])
    title = data.get('title', 'Notebook')
    html_parts = [f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title}</title>']
    html_parts.append('<style>body{background:#0a0a0a;color:#e5e5e5;font-family:monospace;padding:2rem;max-width:900px;margin:auto}')
    html_parts.append('pre{background:#1a1a1a;padding:1rem;border-radius:8px;overflow-x:auto}')
    html_parts.append('hr{border-color:#333;margin:2rem 0}')
    html_parts.append('</style></head><body>')
    html_parts.append(f'<h1>{title}</h1>')
    for c in cells:
        lang = c.get('language', '')
        code = c.get('code', '')
        if lang == 'markdown':
            html_parts.append(f'<div>{code}</div>')
        elif lang == 'html':
            html_parts.append(f'<div>{code}</div>')
        else:
            html_parts.append(f'<pre><code>{code}</code></pre>')
        html_parts.append('<hr>')
    html_parts.append('</body></html>')
    response = make_response('\n'.join(html_parts))
    response.headers['Content-Disposition'] = f'attachment; filename={title}.html'
    response.mimetype = 'text/html'
    return response

# --- History Routes ---
@main_bp.route('/history')
def history_page():
    return render_template('history.html', notebooks=Notebook.query.order_by(Notebook.id.desc()).all())

@main_bp.route('/history/load/<int:id>')
def load_history(id):
    nb = Notebook.query.get_or_404(id)
    return jsonify({"id": nb.id, "title": nb.title, "cells": json.loads(nb.content)})

@main_bp.route('/history/delete/<int:id>', methods=['POST'])
def delete_history(id):
    nb = Notebook.query.get_or_404(id)
    db.session.delete(nb)
    db.session.commit()
    return jsonify({"status": "success"})

@main_bp.route('/history/rename/<int:id>', methods=['POST'])
def rename_history(id):
    nb = Notebook.query.get_or_404(id)
    new_title = request.json.get('title')
    if new_title:
        nb.title = new_title
        db.session.commit()
    return jsonify({"status": "success", "title": nb.title})

@main_bp.route('/history/export/<int:id>')
def export_history(id):
    nb = Notebook.query.get_or_404(id)
    # Create a proper file download response
    json_content = json.dumps({"cells": json.loads(nb.content)}, indent=2)
    response = make_response(json_content)
    # Using .npy so it can be imported back or converted by CLI
    response.headers['Content-Disposition'] = f'attachment; filename={nb.title}.npy'
    response.mimetype = 'application/json'
    return response

# --- Standard Routes ---
@main_bp.route('/')
def home(): return render_template('index.html')

@main_bp.route('/variables')
def variables(): return jsonify(get_variables())

@main_bp.route('/kernel/restart', methods=['POST'])
def restart_kernel():
    PYTHON_GLOBALS.clear()
    return jsonify({"status": "restarted"})

@main_bp.route('/kernel/cancel', methods=['POST'])
def cancel_kernel():
    cancel_execution()
    return jsonify({"status": "cancelled"})

@main_bp.route('/git/clone', methods=['POST'])
def git_clone():
    try:
        url = request.json.get('url')
        Repo.clone_from(url, os.path.join(current_app.config['WORKSPACE'], url.split('/')[-1].replace('.git', '')))
        return jsonify({"status": "success"})
    except Exception as e: return jsonify({"status": "error", "message": str(e)})

@main_bp.route('/save', methods=['POST'])
def save_notebook():
    data = request.json
    title = data.get('title', 'Untitled')
    cells_json = json.dumps(data.get('cells'))
    project_id = data.get('id')

    if project_id:
        # Update existing
        nb = Notebook.query.get(project_id)
        if nb:
            nb.title = title
            nb.content = cells_json
            db.session.commit()
            return jsonify({"status": "updated", "id": nb.id})
    
    # Create new
    nb = Notebook(title=title, content=cells_json)
    db.session.add(nb)
    db.session.commit()
    return jsonify({"status": "saved", "id": nb.id})

# --- Socket Events ---
@socketio.on('connect')
def on_connect():
    global TERMINAL_FD, TERMINAL_PROC
    if HAS_PTY and TERMINAL_FD: return
    if not HAS_PTY and TERMINAL_PROC: return
    if HAS_PTY:
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(current_app.config['WORKSPACE'])
            subprocess.run(["bash"])
            sys.exit(0)
        else:
            TERMINAL_FD = fd
            t = threading.Thread(target=read_and_emit_pty, args=(fd,))
            t.daemon = True
            t.start()
    else:
        shell = 'powershell.exe' if os.system('where pwsh > nul 2>&1') == 0 else 'cmd.exe'
        TERMINAL_PROC = subprocess.Popen([shell], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=current_app.config['WORKSPACE'], shell=True)
        t = threading.Thread(target=read_and_emit_pipe, args=(TERMINAL_PROC,))
        t.daemon = True
        t.start()

@socketio.on('terminal_input')
def on_terminal_input(data):
    global TERMINAL_FD, TERMINAL_PROC
    if HAS_PTY and TERMINAL_FD: os.write(TERMINAL_FD, data['input'].encode())
    elif not HAS_PTY and TERMINAL_PROC:
        TERMINAL_PROC.stdin.write(data['input'].encode())
        TERMINAL_PROC.stdin.flush()

@socketio.on('execute_code')
def handle_execution(data):
    lang = data.get('language')
    cell_id = data.get('cell_id')
    emit('execution_started', {'cell_id': cell_id})
    if lang == 'python': result = run_python_stateful(data.get('code'))
    else: result = {"output": "", "status": "success"} 
    emit('execution_result', {'cell_id': cell_id, 'output': result['output'], 'status': result['status']})
