# Nbook Features

> A comprehensive reference for every major feature in the Nbook Flask web application.

---

## 1. Interactive Code Cells

### Overview

Nbook supports five distinct cell types: **Python**, **JavaScript**, **HTML**, **Bash**, and **Markdown**. Each cell type provides a tailored editing and execution experience. Cells are the fundamental building block of every notebook — users add them via the `+` menu or quick-add PY button in the toolbar, and each appears as a glass-panel card with a language badge, drag handle, run button, and output area.

### Python Cells (Stateful Execution)

Python cells are the core of Nbook. When a user runs a Python cell, the code is sent via Socket.IO to the Flask backend, where `run_python_stateful()` in `core/executor.py:24` executes it within a shared global namespace (`PYTHON_GLOBALS`). This means variables defined in one cell persist and are available in subsequent cells — exactly like a Jupyter notebook. The executor first attempts to `eval()` the code as an expression (printing the result if non-`None`), and falls back to `exec()` on `SyntaxError`, ensuring both expressions like `2 + 2` and statements like `x = 42` work seamlessly.

```python
# core/executor.py
def run_python_stateful(code_str):
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer

    if code_str.strip().startswith('!'):
        cmd = code_str.strip()[1:]
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return {"output": proc.stdout + proc.stderr, "status": "success"}

    try:
        compiled = compile(code_str, '<string>', 'eval')
        result = eval(compiled, PYTHON_GLOBALS)
        if result is not None:
            print(result)
    except SyntaxError:
        exec(code_str, PYTHON_GLOBALS)

    output = buffer.getvalue()
    return {"output": output, "status": "success"}
```

### Magic Commands and Shell Execution

Any cell content starting with `!` is treated as a shell command. The executor strips the `!` prefix and runs the remainder via `subprocess.run()` with a 30-second timeout. This allows users to run `!pip install`, `!ls -la`, or `!echo hello` directly from a Python cell. The output is captured and returned as the cell result.

### Matplotlib Inline Plotting

When a Python cell imports `matplotlib`, the executor injects a custom `_nbook_show()` function that patches `plt.show()`. Instead of opening a GUI window, it saves the plot to a PNG buffer, base64-encodes it, and prints a special `NBOOK_IMG:` token to stdout. The frontend intercepts this token and renders the image inline:

```javascript
// index.html
socket.on('execution_result', d => {
    if(d.output && d.output.includes('NBOOK_IMG:')){
        c.find('.plot-output')
         .html(`<img src="data:image/png;base64,${d.output.split('NBOOK_IMG:')[1].trim()}" class="rounded-lg mt-2">`)
         .removeClass('hidden');
    } else {
        c.find('.output').text(d.output || '');
    }
});
```

### CodeMirror Editor

Each cell contains a `<textarea>` that is instantiated as a CodeMirror editor. The editor provides syntax highlighting, line numbers, bracket matching, and autocomplete via `Ctrl-Space`. The mode is chosen based on the language: `python`, `htmlmixed`, `markdown`, `javascript`, or `shell`. The editor theme is configurable globally through the Settings page and supports Palenight, Darcula, Monokai, Solarized, and Default.

### Execution Cancellation

Users can cancel a running Python execution by clicking the **STOP** button, which calls `POST /kernel/cancel`. The executor checks a `threading.Event()` flag (`_cancel_flag`) before executing each cell. If set, execution is aborted and globals are cleared:

```python
def cancel_execution():
    _cancel_flag.set()
```

### Non-Python Cell Types

- **JavaScript**: Executed client-side via `eval()`. Console output is captured by overriding `console.log`, `console.warn`, and `console.error`.
- **HTML**: Rendered directly into a preview area within the cell using jQuery's `.html()`.
- **Markdown**: Parsed client-side by the `marked` library and rendered with a prose style.
- **Bash**: Sent to the server and executed via `subprocess.run()`, same as the `!` magic command.

---

## 2. Integrated Terminal

### Overview

The terminal tab in the sidebar provides a full terminal emulator using **Xterm.js** (v5.3.0) with the **fit addon** for responsive sizing. It is available on the main editor page and provides shell access directly within the browser.

### Server-Side Architecture

On the server, the terminal is initialized when a Socket.IO connection is established (`core/routes.py:380-404`). The implementation branches based on platform:

- **Unix (PTY)**: Uses `pty.fork()` to spawn a `bash` process. A daemon thread reads from the PTY file descriptor in a loop (100ms intervals) and emits `terminal_output` events via Socket.IO.
- **Windows (Subprocess)**: Detects `pwsh` (PowerShell 7+) availability; falls back to `cmd.exe`. Uses `subprocess.Popen` with piped stdin/stdout and a daemon thread for reading.

```python
# core/routes.py - Terminal initialization (Socket.IO connect)
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
    TERMINAL_PROC = subprocess.Popen([shell], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        cwd=current_app.config['WORKSPACE'], shell=True)
    t = threading.Thread(target=read_and_emit_pipe, args=(TERMINAL_PROC,))
    t.daemon = True
    t.start()
```

### Frontend Integration

The terminal is initialized lazily — it only starts when the user clicks the **TERM** tab for the first time. The Xterm.js instance listens for user input via `term.onData()` and forwards it to the server via `terminal_input` Socket.IO events. Server output is received via `terminal_output` events and written to the terminal:

```javascript
function initTerminal() {
    if(term) return;
    term = new Terminal({
        theme: { background: '#000000' },
        fontFamily: 'Fira Code',
        fontSize: 12,
        cursorBlink: true,
        rows: 20
    });
    fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal-container'));
    fitAddon.fit();
    term.onData(d => socket.emit('terminal_input', { input: d }));
    socket.on('terminal_output', d => term.write(d.output));
}
```

### Shell Auto-Detection on Windows

On Windows, Nbook checks for `pwsh` availability. If found, PowerShell 7+ is used; otherwise it falls back to `cmd.exe`. This ensures the best possible terminal experience regardless of the Windows configuration.

---

## 3. File Explorer

### Overview

The file explorer is the default sidebar tab, providing full CRUD operations on files and folders within the workspace directory (`./workspace/`). It renders a tree-like listing with icons for files and folders, hover actions (open, download, rename, delete), and navigation through directories.

### Browsing and Directory Traversal

The file list is fetched via `GET /files/list?path=<relative_path>`. The server resolves the path safely using `get_safe_path()`, which joins the workspace root with the requested path and checks that the result is within the workspace (preventing path traversal attacks). Files starting with `.` are hidden. Results are sorted with directories first, then alphabetically.

```python
# core/routes.py - Path traversal protection
def get_safe_path(req_path):
    workspace = os.path.abspath(current_app.config['WORKSPACE'])
    target = os.path.abspath(os.path.join(workspace, req_path.strip('/')))
    return target if target.startswith(workspace) else None
```

### File Operations

| Action | Endpoint | Method |
|--------|----------|--------|
| List | `/files/list` | GET |
| Read | `/files/read` | GET |
| Create | `/files/create` | POST |
| Delete | `/files/delete` | POST |
| Rename | `/files/rename` | POST |
| Upload | `/files/upload` | POST |
| Download | `/files/download` | GET |
| Save | `/save-file` | POST |

- **Create**: Accepts `type: "file"` or `type: "directory"`. Directories are created with `os.makedirs()`, files with a simple `open(path, 'w')`.
- **Delete**: Uses `shutil.rmtree()` for directories and `os.remove()` for files.
- **Rename**: Renames via `os.rename()`. Checks for name collisions.
- **Upload**: Accepts multipart file uploads. Filenames are sanitized with `_safe_filename()` which strips directory components via `os.path.basename()`.

### Blocked Extension Whitelist

Uploaded files are checked against a blocked extension set:

```python
BLOCKED_EXTENSIONS = {'.exe', '.bat', '.cmd', '.com', '.msi', '.scr', '.pif',
                      '.sh', '.pyc', '.dll', '.so', '.dylib', '.vbs', '.ps1', '.app'}
```

If the uploaded file's extension matches any of these, the upload is rejected with a 400 error. This prevents executable uploads from compromising the server.

### File Editor Modal

Clicking a file in the explorer opens an in-browser editor modal. The file content is fetched via `/files/read`, displayed in a `<textarea>`, and can be saved back via `POST /save-file`. The editor supports UTF-8 text files and rejects binary files based on MIME type detection.

---

## 4. Project Management

### Overview

Nbook notebooks are persisted to an **SQLite database** via Flask-SQLAlchemy. The `Notebook` model has three fields: `id` (int, primary key), `title` (string), and `content` (text, storing JSON-serialized cell data). A `User` foreign key (`user_id`) provides optional per-user scoping.

### Saving Notebooks

The `POST /save` endpoint accepts a title, cell array, and optional project ID. If an ID is provided and the notebook exists, it is updated. Otherwise, a new notebook is created. The frontend calls `saveProject()` to send this data. On success, the returned `id` is stored in `loadId` for subsequent saves.

```javascript
function saveProject(silent) {
    const title = $('#nb-title').val();
    const cells = [];
    for(let id in editors)
        cells.push({ code: editors[id].getValue(), language: $(`#${id} .lang-tag`).text().toLowerCase() });
    const payload = { title, cells };
    if(loadId) payload.id = loadId;
    $.ajax({
        url: '/save', type: 'POST', contentType: 'application/json',
        data: JSON.stringify(payload),
        success: (res) => { loadId = res.id; if(!silent) alert(`Saved! ID: ${res.id}`); }
    });
}
```

### Auto-Save

An interval timer in the frontend calls `saveProject(true)` every 30 seconds if any editors are active. The `silent` parameter suppresses the alert dialog during auto-saves, making them invisible to the user:

```javascript
setInterval(() => {
    if(Object.keys(editors).length > 0) saveProject(true);
}, 30000);
```

### Project History Page

The `/history` page renders an HTML template showing all saved notebooks, newest first. Each item displays the title, ID, and action buttons:

- **OPEN**: Redirects to the editor with `?load_id=<id>`, which loads the notebook and sets `collabRoom` for real-time collaboration.
- **RENAME**: Prompts for a new name via `POST /history/rename/<id>`.
- **EXPORT**: Downloads the notebook as `.npy` via `GET /history/export/<id>`.
- **DELETE**: Deletes with confirmation via `POST /history/delete/<id>`.

### Loading Projects by ID

The editor page accepts a `?load_id=<id>` query parameter. On page load, it fetches cell data via `GET /history/load/<id>`, sets the title, and recreates each cell:

```javascript
if(loadId) {
    collabJoin(`nb-${loadId}`);
    $.get(`/history/load/${loadId}`, (data) => {
        $('#nb-title').val(data.title);
        data.cells.forEach(c => addCell(c.language, c.code));
    }).fail(() => addCell('python'));
}
```

---

## 5. Export

### Overview

Nbook provides three export formats, accessible from both the main editor sidebar and the Settings page. Each format produces a downloadable file with the notebook title as the filename.

### JSON Export (.npy)

The `downloadJSON()` function on the frontend serializes all cells into a JSON object with `{ cells: [...] }` and triggers a download as `project.npy`. The server-side export at `/history/export/<id>` creates the same format from a saved notebook. The `.npy` extension is used so files can be imported back or converted via the CLI.

```javascript
function downloadJSON() {
    const cells = [];
    for(let id in editors)
        cells.push({ code: editors[id].getValue(), language: $(`#${id} .lang-tag`).text().toLowerCase() });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify({cells}, null, 2)], {type: "application/json"}));
    a.download = "project.npy";
    a.click();
}
```

### HTML Export

The `POST /export/html` endpoint generates a standalone HTML document with a dark theme. It wraps the cells in `<pre><code>` blocks for code cells, renders markdown and HTML cells directly as `<div>` elements, and includes inline CSS for the dark background, monospace font, and styling:

```python
# core/routes.py:224-248
html_parts = [
    f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>',
    '<style>body{background:#0a0a0a;color:#e5e5e5;font-family:monospace;padding:2rem;max-width:900px;margin:auto}</style>',
    '</head><body>',
    f'<h1>{title}</h1>'
]
for c in cells:
    lang = c.get('language', '')
    code = c.get('code', '')
    if lang == 'markdown' or lang == 'html':
        html_parts.append(f'<div>{code}</div>')
    else:
        html_parts.append(f'<pre><code>{code}</code></pre>')
    html_parts.append('<hr>')
```

### PDF Export

The `POST /export/pdf` endpoint uses **fpdf2** (`from fpdf import FPDF`) to generate a PDF. It uses Courier font (monospace) exclusively, meaning no system fonts are required — the PDF renders correctly on any platform. Each cell is printed with a language header in gray and the code in light gray at 8pt. Lines are encoded to latin-1 (with `replace` for non-ASCII characters) to prevent encoding errors:

```python
# core/routes.py:250-282
pdf = FPDF()
pdf.add_page()
pdf.set_font('Courier', 'B', 16)
pdf.cell(0, 10, title[:60], new_x='LMARGIN', new_y='NEXT')
for c in cells:
    lang = c.get('language', 'python')
    code = c.get('code', '')
    pdf.set_font('Courier', 'B', 10)
    pdf.cell(0, 6, f'[{lang.upper()}]', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Courier', '', 8)
    for line in code.split('\n'):
        pdf.cell(0, 4, line[:100], new_x='LMARGIN', new_y='NEXT')
```

The PDF response is served as `application/pdf` with a `Content-Disposition` attachment header.

---

## 6. User Authentication

### Overview

Nbook provides a complete session-based authentication system in `core/auth.py`. Users can register, log in, log out, and edit their profile. The system uses **werkzeug.security** for password hashing (`generate_password_hash` / `check_password_hash`) and Flask sessions for tracking login state.

### User Model

The `User` model (`core/models.py:4-15`) stores `id`, `username` (unique, required), `password_hash`, `full_name`, and `email`. Passwords are never stored in plain text:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default='')
    email = db.Column(db.String(120), default='')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Registration

`POST /auth/register` accepts `username`, `password`, `confirm_password`, `full_name`, and `email` (via JSON or form data). Validation checks include:
- Username and password are required
- Passwords must match
- Password must be at least 4 characters
- Username and email must be unique

On success, the user is created, automatically logged in (session variables are set), and a JSON response is returned.

### Login and Logout

`POST /auth/login` validates credentials against the database and sets `session['user_id']` and `session['username']`. `POST /auth/logout` clears the session entirely. The `GET /auth/me` endpoint returns the current user's authentication status and details, used by the frontend to update the UI:

```javascript
function checkAuth() {
    $.get('/auth/me', (res) => {
        if(res.authenticated) {
            $('#auth-username').text(res.username);
            $('#auth-buttons').addClass('hidden');
            $('#logout-btn').removeClass('hidden');
        } else {
            $('#auth-username').text('Not logged in');
            $('#auth-buttons').removeClass('hidden');
            $('#logout-btn').addClass('hidden');
        }
    });
}
```

### Profile Editing

The `/auth/profile` page (GET for the form, POST for updates) allows authenticated users to update their `full_name`, `email`, and optionally change their password. Password change requires confirmation matching and a minimum length of 4 characters. The page also shows the username (read-only).

---

## 7. Settings Page

### Overview

The Settings page (`/settings`) provides a control panel for system monitoring, kernel management, theming, and project export. It is served by `render_template('settings.html')` with all notebooks passed as context.

### System Status with RAM and Disk Bars

The settings page displays real-time RAM and disk usage as progress bars, fetched from `GET /system/stats`. The server uses the `psutil` library to query memory (`psutil.virtual_memory()`) and disk usage (`psutil.disk_usage()` on the workspace directory). CPU percentage is also collected via `psutil.cpu_percent()`:

```python
@main_bp.route('/system/stats')
def system_stats():
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(current_app.config['WORKSPACE'])
    return jsonify({
        "status": "online",
        "cpu": psutil.cpu_percent(interval=None),
        "ram": {"percent": mem.percent, "used": round(mem.used / (1024**3), 2), "total": round(mem.total / (1024**3), 2)},
        "disk": {"percent": disk.percent, "used": round(disk.used / (1024**3), 2), "total": round(disk.total / (1024**3), 2)}
    })
```

The frontend polls this endpoint every 5 seconds on the settings page and every 2 seconds on the main editor page.

### Kernel Restart

The **RESTART KERNEL** button sends `POST /system/restart`, which clears `PYTHON_GLOBALS` and calls `cancel_execution()`. This effectively resets the Python execution state, clearing all user-defined variables and imported modules.

### Global CodeMirror Theme Selector

A `<select>` dropdown allows users to choose from five CodeMirror themes: **Palenight (Dark)**, **Darcula**, **Monokai**, **Solarized**, and **Light (Default)**. The selection is persisted to `localStorage` under the key `nbook-cm-theme` and applies to all editors immediately via `setGlobalCMTheme()`:

```javascript
function setGlobalCMTheme(theme) {
    settingsCMTheme = theme;
    localStorage.setItem('nbook-cm-theme', theme);
}
```

### Project Export Selector

The settings page includes a `<select>` populated with all saved notebooks, plus export buttons for JSON, HTML, and PDF formats. Selecting a project and clicking an export button loads the project data and triggers the appropriate export endpoint.

---

## 8. Collaborative Editing

### Overview

Nbook uses **Socket.IO rooms** to enable real-time collaborative editing. When a notebook is loaded via a `load_id`, a room is created with the name `nb-<id>`. All users viewing the same notebook are joined to the same room and receive broadcast events.

### Room Join/Leave

The client calls `collabJoin()` on page load (if a `load_id` is present), which emits `join_notebook` with the room name. Similarly, `collabLeave()` is called on new project creation:

```javascript
function collabJoin(room) {
    collabRoom = room;
    socket.emit('join_notebook', { room });
}
function collabLeave() {
    if(collabRoom) socket.emit('leave_notebook', { room: collabRoom });
    collabRoom = null;
}
```

### Broadcast Events

Five Socket.IO events are broadcast to all room participants (excluding the sender via `include_self=False`):

| Event | Data | Trigger |
|-------|------|---------|
| `cell_edit` | `cell_id, code, language, cursor` | Editor change (500ms debounce) |
| `cell_add` | `cell_id, language, code` | New cell created |
| `cell_delete` | `cell_id` | Cell deleted |
| `cell_reorder` | `order` (array of IDs) | Drag-and-drop reorder |
| `nb_title` | `title` | Title input change |

```python
# core/routes.py - Collaborative broadcast handlers
@socketio.on('cell_edit')
def on_cell_edit(data):
    room = data.get('room', 'global')
    emit('cell_edit', data, room=room, include_self=False)
```

### Client-Side Merging

When a `cell_edit` event is received, the client checks if the editor exists, sets an `isCollabEdit` flag to prevent echo broadcasts, updates the CodeMirror value, restores the cursor position, then clears the flag:

```javascript
socket.on('cell_edit', d => {
    if(!d.cell_id || !editors[d.cell_id]) return;
    isCollabEdit = true;
    const cm = editors[d.cell_id];
    cm.setValue(d.code);
    if(d.cursor) cm.setCursor(d.cursor);
    isCollabEdit = false;
});
```

### Real-Time Cell Reordering

When cells are dragged and dropped, the client collects the new order of cell IDs and broadcasts it via `cell_reorder`. Receiving clients re-append elements to the container in the specified order, maintaining visual consistency across all participants.

---

## 9. Keyboard Shortcuts

### Overview

Nbook defines four global keyboard shortcuts via a jQuery `keydown` handler on the document. These shortcuts work across the entire editor interface.

| Shortcut | Action | Implementation |
|----------|--------|----------------|
| **Ctrl+Enter** | Run the last cell | Finds the last `.glass-panel` cell, determines its language, and calls `runCell()` |
| **Ctrl+Shift+Enter** | Run the last cell, then add a new Python cell | Runs the cell and immediately calls `addCell('python')` |
| **Ctrl+S** | Save the project | Calls `saveProject()` (with `silent=false`) |
| **Ctrl+Shift+N** | New project | Calls `newProject()` which clears all cells and prompts for confirmation |

```javascript
$(document).on('keydown', (e) => {
    const isMeta = e.ctrlKey || e.metaKey;
    if (isMeta && e.key === 'Enter') {
        e.preventDefault();
        const $cell = $('.glass-panel:last');
        if ($cell.length) {
            const id = $cell.attr('id');
            const lang = $(`#${id} .lang-tag`).text().toLowerCase();
            runCell(id, lang);
        }
    }
    if (isMeta && e.shiftKey && e.key === 'Enter') {
        e.preventDefault();
        const $cell = $('.glass-panel:last');
        if ($cell.length) {
            const id = $cell.attr('id');
            const lang = $(`#${id} .lang-tag`).text().toLowerCase();
            runCell(id, lang);
            addCell('python');
        }
    }
    if (isMeta && e.key === 's') { e.preventDefault(); saveProject(); }
    if (isMeta && e.shiftKey && e.key === 'N') { e.preventDefault(); newProject(); }
});
```

The shortcuts use `e.ctrlKey || e.metaKey` for cross-platform compatibility (Ctrl on Windows/Linux, Cmd on macOS). All shortcuts call `e.preventDefault()` to prevent browser default behavior.

---

## 10. Cell Management

### Overview

Nbook provides a set of cell management features including drag-and-drop reordering, per-cell undo/redo, a cell search filter, and cell deletion — all within the browser.

### Drag-and-Drop Reorder

Each cell has a **drag handle** (six-dot grid icon) in its header. The handle is a `draggable="true"` element. The frontend tracks the source cell via `_dragSrcId` on `dragstart`, applies visual feedback during `dragover`, and rearranges the DOM on `drop`. After reordering, the new order is broadcast to collaborators:

```javascript
$(document).on('drop', '#notebook-container', function(e) {
    e.preventDefault();
    if(!_dragSrcId) return;
    const target = $(e.target).closest('.glass-panel');
    if(!target.length || target.attr('id') === _dragSrcId) return;
    const $src = $(`#${_dragSrcId}`);
    const pos = target.index();
    const srcPos = $src.index();
    if(srcPos < pos) target.after($src);
    else target.before($src);
    const order = [];
    $('#notebook-container').find('.glass-panel[id^="cell-"]').each(function() { order.push($(this).attr('id')); });
    collabEmit('cell_reorder', { order });
});
```

### Per-Cell Undo/Redo

CodeMirror natively supports undo/redo. Nbook exposes this with the **Undo** and **Redo** buttons in the main toolbar, which call `editors[id].undo()` and `editors[id].redo()` on every open editor:

```javascript
function undoCell() { for(let id in editors) { editors[id].undo(); } }
function redoCell() { for(let id in editors) { editors[id].redo(); } }
```

Additionally, each cell has an individual undo button that operates only on that specific cell.

### Cell Search Filter

A search input field in the main toolbar (`id="search-cell"`) filters visible cells in real-time. On every keystroke, it iterates through all cell panels, checks whether the cell's CodeMirror content or language tag contains the query text, and toggles visibility:

```javascript
$(document).on('input', '#search-cell', function() {
    const q = $(this).val().toLowerCase();
    $('.glass-panel[id^="cell-"]').each(function() {
        const id = $(this).attr('id');
        const code = editors[id] ? editors[id].getValue().toLowerCase() : '';
        const lang = $(this).find('.lang-tag').text().toLowerCase();
        $(this).toggle(code.includes(q) || lang.includes(q));
    });
});
```

### Cell Delete

Each cell has an **X** button (close icon) in its header. Clicking it removes the cell from the DOM, deletes the editor from the `editors` object, and broadcasts the deletion to collaborators:

```javascript
function deleteCell(id) {
    if(!editors[id]) return;
    collabEmit('cell_delete', { cell_id: id });
    $(`#${id}`).remove();
    delete editors[id];
}
```

---

## 11. Theming

### Overview

Nbook supports a dark/light mode toggle and a separate CodeMirror editor theme selector. Both preferences are persisted in `localStorage` and apply immediately across all pages.

### Dark/Light Mode

The `toggleTheme()` function switches between `'dark'` and `'light'` values, stores the preference in `localStorage('nbook-theme')`, and calls `applyTheme()`. The function toggles the `dark` class on the `<html>` element (Tailwind CSS dark mode), sets body `background-color` and `color`, updates the theme button text, and reapplies the CodeMirror theme to all editors:

```javascript
function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('nbook-theme', currentTheme);
    applyTheme();
}
function applyTheme() {
    const isDark = currentTheme === 'dark';
    $('html').attr('class', isDark ? 'dark' : '');
    document.body.style.backgroundColor = isDark ? '#0a0a0a' : '#ffffff';
    document.body.style.color = isDark ? '#e5e5e5' : '#1a1a1a';
    const activeCMTheme = cmTheme || (isDark ? 'material-palenight' : 'default');
    for(let id in editors) { editors[id].setOption('theme', activeCMTheme); }
}
```

### CodeMirror Themes

Five CodeMirror themes are included via CDN stylesheets in `base.html`:

```html
<link rel="stylesheet" href=".../theme/material-palenight.min.css">
<link rel="stylesheet" href=".../theme/darcula.min.css">
<link rel="stylesheet" href=".../theme/monokai.min.css">
<link rel="stylesheet" href=".../theme/solarized.min.css">
<link rel="stylesheet" href=".../theme/default.min.css">
```

The user selects a theme from the Settings page dropdown. The value is stored in `localStorage('nbook-cm-theme')` and applied to all CodeMirror instances. Available themes are: **Palenight** (default dark), **Darcula**, **Monokai**, **Solarized**, and **Default** (light).

### Persistence

Both `nbook-theme` and `nbook-cm-theme` are read from `localStorage` on every page load (or initialization) and from the Settings page, ensuring the user's visual preferences survive page refreshes and browser restarts.

---

## 12. Security

### Overview

Nbook implements multiple layers of security: rate limiting, HTTP security headers, API key authentication, file validation, and secure cookie configuration.

### Rate Limiting

Nbook uses **Flask-Limiter** with a default limit of 200 requests per minute and 20 requests per second, keyed by remote IP address:

```python
# app.py
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute", "20 per second"])
```

This is applied globally to all routes, protecting against brute-force and abuse attacks.

### Content Security Policy (CSP)

A comprehensive CSP header is set on every response via an `after_request` handler. It restricts script sources to `'self'`, CDNs (`cdnjs.cloudflare.com`, `cdn.jsdelivr.net`, etc.), and allows `'unsafe-inline'` and `'unsafe-eval'` (required by CodeMirror and Tailwind). Connect sources include `ws:` and `wss:` for WebSocket connections:

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com ... 'unsafe-inline' 'unsafe-eval'; connect-src 'self' ws: wss:"
    return response
```

### API Key Authentication (Secure Mode)

When `NBOOK_MODE` is set to `'secure'`, every request (except static files and Socket.IO) is checked for a valid API key. The key can be provided as a query parameter (`?key=...`) or as an `X-API-KEY` header. Invalid or missing keys result in a 403 error:

```python
@main_bp.record_once
def register_middleware(state):
    @state.app.before_request
    def check_api_key():
        if current_app.config.get('NBOOK_MODE') == 'secure':
            key = request.args.get('key') or request.headers.get('X-API-KEY')
            if key != current_app.config.get('NBOOK_API_KEY'):
                abort(403)
```

The secure mode key is a UUID generated at startup and printed to the console. Socket.IO connections also validate the key via query parameter.

### File Upload Whitelist

Uploaded files are checked against `BLOCKED_EXTENSIONS` (executable and script file types). Additionally, a 50MB upload size limit is configured via `MAX_CONTENT_LENGTH`. Filenames are sanitized to remove directory components, preventing path injection.

### Other Security Headers

- **`X-Content-Type-Options: nosniff`** — Prevents MIME type sniffing.
- **`X-Frame-Options: DENY`** — Prevents clickjacking by blocking framing.
- **`X-XSS-Protection: 1; mode=block`** — Enables browser XSS filter.
- **`SESSION_COOKIE_SAMESITE = 'Lax'`** — Prevents CSRF via same-site cookie restriction.
- **`SESSION_COOKIE_HTTPONLY = True`** — Prevents JavaScript access to session cookies.

---

## 13. Git Integration

### Overview

Nbook allows users to clone Git repositories directly into the workspace from the sidebar's **GIT** tab. This feature is powered by the **GitPython** library.

### Clone from URL

The GIT tab provides a text input for a repository URL and a **CLONE REPO** button. When clicked, the frontend sends a POST request to `/git/clone` with the URL:

```javascript
function cloneRepo() {
    const u = $('#repo-url').val();
    if(u) $.ajax({
        url: '/git/clone', type: 'POST', contentType: 'application/json',
        data: JSON.stringify({ url: u }),
        success: r => { alert(r.status); loadFiles(); }
    });
}
```

### Server-Side Cloning

The server uses `git.Repo.clone_from()` to clone the repository into the workspace directory. The repository name is extracted from the URL by taking the last segment (minus `.git`):

```python
@main_bp.route('/git/clone', methods=['POST'])
def git_clone():
    try:
        url = request.json.get('url')
        Repo.clone_from(url, os.path.join(
            current_app.config['WORKSPACE'],
            url.split('/')[-1].replace('.git', '')
        ))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
```

After cloning, the frontend refreshes the file explorer to show the newly cloned repository contents.

---

## 14. Docker Support

### Overview

Nbook includes a `Dockerfile` and `docker-compose.yml` for containerized deployment. The image is based on `python:3.11-slim` and exposes port 52896.

### Dockerfile

The Dockerfile installs dependencies from `requirements.txt`, copies the application code, and defaults to running in free mode:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 52896
ENV FLASK_ENV=production
ENV NBOOK_PORT=52896
CMD ["python", "app.py", "free"]
```

### Docker Compose

The `docker-compose.yml` mounts two named volumes (`data` and `workspace`) for persistent storage and optionally mounts a `.env` file for configuration:

```yaml
version: "3.9"
services:
  nbook:
    build: .
    container_name: nbook
    ports:
      - "52896:52896"
    volumes:
      - ./data:/app/data
      - ./workspace:/app/workspace
      - ./.env:/app/.env:ro
    environment:
      - NBOOK_MODE=free
      - NBOOK_PORT=52896
    restart: unless-stopped
```

The `restart: unless-stopped` policy ensures the container automatically restarts after a crash or system reboot. Volumes persist notebooks and workspace files across container restarts.

---

## 15. CI/CD

### Overview

Nbook uses **GitHub Actions** for continuous integration. The workflow file at `.github/workflows/tests.yml` runs on every push and pull request to the `main` branch.

### Workflow Configuration

The test matrix runs across three Python versions (3.10, 3.11, 3.12) on `ubuntu-latest`. The workflow has three steps: checkout, dependency installation, and test execution:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest
      - name: Run tests
        run: python -m pytest tests/ -v
      - name: Check app starts
        run: timeout 10 python -c "from app import create_app; app = create_app(); print('App starts OK')"
```

### What Gets Tested

The test suite (`tests/`) contains 27+ tests across three files:

- **`test_routes.py`** (13 tests): Verifies home page rendering, system stats endpoint, variable listing, file listing, history page, 404 handling, kernel restart/cancel, save/load notebook cycle, file CRUD operations, and secure mode access control.
- **`test_executor.py`** (12 tests): Covers simple print, eval expressions, variable persistence between cells, syntax errors, runtime errors, magic commands (`!`), cancellation before execution, variable introspection, private variable exclusion, matplotlib injection detection, and globals clearing on restart.
- **`test_terminal.py`** (3 tests): Tests the `convert_notebook()` function for file-not-found, invalid JSON, and valid notebook conversion to code folders.

The final step validates that the Flask application factory `create_app()` executes without errors, ensuring the app boots successfully.
