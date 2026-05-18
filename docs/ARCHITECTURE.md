# Nbook Architecture

Nbook is a modern web-based interactive notebook environment. It uses Flask for the backend, Flask-SocketIO for real-time communication, and a rich JavaScript frontend (CodeMirror, Xterm.js, jQuery, Tailwind CSS) for an interactive user experience.

## 1. Overall System Design

The architecture follows a client-server model with real-time interaction:

- **Client (Browser):** Renders the UI, handles user input (code, terminal, file ops), communicates via HTTP (page loads, file uploads/downloads) and WebSockets (code execution, terminal I/O, collaboration).
- **Server (Flask Application):** Manages application state, handles HTTP requests, manages WebSocket connections, executes Python code statefully, interacts with the filesystem, persists data in SQLite, and provides a CLI.

```
Client Browser
  │
  ├── HTTP ──► Flask App ──► SQLite DB
  │                 │
  │                 ├── Workspace Filesystem
  │                 ├── GitPython (clone)
  │                 └── psutil (system stats)
  │
  └── WebSocket ──► Socket.IO
                       │
                       ├── Python Executor (stateful globals)
                       ├── Terminal (PTY/subprocess)
                       └── Collaboration Rooms
```

## 2. Core Modules (`core/`)

### `core/__init__.py`
Initializes Flask extensions: `SQLAlchemy` for the database, `SocketIO` for WebSocket communication. Imports the `Notebook` model.

### `core/models.py`
SQLAlchemy models:
- **User:** `id`, `username`, `password_hash`, `full_name`, `email`. Methods: `set_password()`, `check_password()` using werkzeug.
- **Notebook:** `id`, `title`, `content` (JSON string of cells), `user_id` (FK to User).

### `core/auth.py`
Authentication blueprint (`/auth`):
- `POST /auth/register` — Create account with username, password, confirm_password, full_name, email
- `POST /auth/login` — Authenticate and create session
- `POST /auth/logout` — Clear session
- `GET /auth/me` — Return authenticated user info
- `GET/POST /auth/profile` — View/edit profile and change password

Uses Flask sessions for auth state. Passwords hashed with `werkzeug.security.generate_password_hash`.

### `core/routes.py`
Main blueprint with all HTTP endpoints and Socket.IO event handlers:

**HTTP Routes (categorized):**
- **System:** `/system/stats` (psutil RAM/disk/CPU), `/system/restart` (clear kernel)
- **Files:** `/files/list`, `/files/read`, `/files/delete`, `/files/rename`, `/files/create`, `/files/upload`, `/files/download`, `/save-file`
- **Projects:** `/save`, `/history`, `/history/load/<id>`, `/history/delete/<id>`, `/history/rename/<id>`, `/history/export/<id>`
- **Export:** `/export/html`, `/export/pdf` (fpdf2)
- **Kernel:** `/kernel/restart`, `/kernel/cancel`, `/variables`
- **Git:** `/git/clone`
- **Pages:** `/` (editor), `/history`, `/settings`

**Socket.IO Events:**
- `execute_code` → `execution_result` — Run Python code in stateful globals
- `terminal_input` → `terminal_output` — Bi-directional terminal I/O
- `join_notebook` / `leave_notebook` — Collaboration room management
- `cell_edit` / `cell_add` / `cell_delete` / `cell_reorder` / `nb_title` — Real-time collaboration broadcast

**Security Middleware:**
- `check_api_key()` registered via `@main_bp.record_once` for Flask 3.x compatibility
- Blocks requests in secure mode if API key is missing

### `core/executor.py`
Stateful Python code executor:
- Maintains `PYTHON_GLOBALS` dict across cell executions
- Supports magic commands (`!` prefix = shell execution)
- Injects matplotlib patch to capture plots as base64 images
- Captures stdout via `io.StringIO` buffer
- Supports cancellation via `threading.Event`

### `core/cli.py`
Click CLI with three commands:
- `python app.py start` — Secure mode with auto-generated API key
- `python app.py free` — Free mode, no auth required
- `python app.py convert <file>` — Convert .npy/.ngo to code folder

### `core/terminal.py`
Server runners and notebook converter:
- `run_server_secure()` — Sets secure mode, generates API key, starts Socket.IO server
- `run_server_free()` — Sets free mode, starts Socket.IO server
- `convert_notebook()` — Extracts cells into separate files by language

### `core/utils.py`
Shared utility functions (path safety, etc.)

## 3. Frontend (`templates/`)

### `base.html`
Base layout with:
- Tailwind CSS (CDN), Google Fonts (VT323, Inter, Fira Code)
- CodeMirror with multiple themes (Palenight, Darcula, Monokai, Solarized, Default)
- Marked.js for Markdown rendering
- jQuery + Socket.IO client
- Responsive CSS breakpoints (768px, 480px)
- Sidebar collapse/expand CSS

### `index.html`
Main editor page (769 lines of HTML + JavaScript):
- **Sidebar:** Project title, auth info, theme/settings/profile nav, file/term/vars/git tabs, save/export buttons, collapse toggle
- **Header:** Notebook title, cell search, RAM/DISK bars, connection status, undo/redo, restart, cell type buttons
- **Notebook Area:** Dynamic cell container with drag-and-drop
- **Mobile:** Hamburger menu overlay, FAB for adding cells
- **JavaScript:** Cell CRUD, CodeMirror editors, socket event handlers, collaborative editing, keyboard shortcuts, auto-save, drag-and-drop, file editor modal, theme toggle, export functions

### `login.html`, `register.html`
Auth pages with glass-panel UI, AJAX form submission.

### `profile.html`
Profile editor: view/edit full_name, email, change password.

### `settings.html`
Settings page: system status (live RAM/disk), kernel restart, global CM theme selector, project selector with JSON/HTML/PDF export buttons.

### `history.html`
Project history page: table of saved notebooks with load/rename/delete/export actions.

### `error.html`
Dynamic error pages for 403, 404, 500 with template variables (`code`, `message`, `detail`).

## 4. Database Schema

### User
| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| username | String(80) | Unique, Not Null |
| password_hash | String(256) | werkzeug hash |
| full_name | String(120) | Optional |
| email | String(120) | Optional |

### Notebook
| Column | Type | Notes |
|--------|------|-------|
| id | Integer | Primary Key |
| title | String(100) | |
| content | Text | JSON array of cells |
| user_id | Integer | FK → user.id, nullable |

## 5. Security Model

Two operational modes:

**Free Mode** (`python app.py free`):
- No authentication required
- Suitable for local development

**Secure Mode** (`python app.py start`):
- Auto-generates UUID API key on startup
- All API requests require `?key=` or `X-API-KEY` header
- Socket.IO connections validate key on connect (return `False` to reject)
- Rate limiting: 200 requests/minute, 20/second (Flask-Limiter)
- Security headers: CSP, X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- File uploads: extension whitelist blocks executables
- Path traversal prevention via `get_safe_path()`
- 50MB max upload size
- Session cookies: SameSite=Lax, HttpOnly

## 6. Workspace Management

All user files reside under `WORKSPACE_DIR` (default: `workspace/`). The `get_safe_path()` function resolves absolute paths and ensures they stay within the workspace, preventing directory traversal attacks.

## 7. Terminal Architecture

The integrated terminal uses a pseudo-terminal (PTY) on Unix via the `pty` module. On Windows, it falls back to `subprocess.Popen` with `pwsh.exe` or `cmd.exe`. Terminal I/O flows over WebSocket:

1. Client sends keystrokes via `terminal_input` event
2. Server writes to PTY/process stdin
3. A background thread reads stdout (1024-byte chunks) and emits `terminal_output` events
4. Xterm.js renders output in the browser

## 8. Export System

- **HTML export:** Generates a dark-themed HTML document from cells
- **PDF export:** Uses `fpdf2` (pure Python, no system dependencies) to generate PDF with Courier font
- **JSON export:** Dumps cells as `.npy` format

## 9. Collaborative Editing

Socket.IO rooms enable real-time collaboration:
- Clients join a room with `join_notebook {room: "nb-<id>"}`
- Cell edits are debounced (500ms) and broadcast to the room excluding the sender
- Cell add/delete/reorder and title changes are broadcast immediately
- Receiving clients update their local state without re-emitting
