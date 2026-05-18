# N-BOOK

**The Glass Interface Notebook** — a stateful, real-time, browser-based interactive notebook built with Flask and Socket.IO.

![Tests](https://github.com/anomalyco/nbook/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

N-BOOK is a web-based interactive notebook that brings the power of stateful Python execution, multi-language cell support, and real-time collaboration to your browser. Inspired by tools like Jupyter Notebook but rebuilt from the ground up with a modern "glass" UI, N-BOOK supports code execution across Python, JavaScript, HTML, Markdown, and Bash — all within a single document. It includes an integrated terminal (powered by Xterm.js via WebSocket), a full file explorer, Git clone support, user authentication, project history with save/load/rename/delete/export, collaborative editing via Socket.IO rooms, and export to JSON, HTML, and PDF.

---

## Features

-  **Stateful Python Execution** — Variables persist across cells; matplotlib plots render inline as base64 images
-  **Multi-Language Cells** — Python, JavaScript, HTML, Markdown, and Bash cell types in one notebook
-  **Integrated Terminal** — Full Xterm.js terminal backed by a PTY (or subprocess on Windows) over WebSocket
-  **File Explorer** — Browse, upload, download, create, rename, and delete files within the workspace directory
-  **In-Browser File Editor** — Edit any text file directly in the browser via a modal editor
-  **Git Clone Support** — Clone any public GitHub repository into the workspace with one click
-  **User Authentication** — Register, login, logout, and profile management (update name, email, password)
-  **Project History** — Save, load, rename, delete, and export projects from a persistent SQLite database
-  **Export Formats** — Export notebooks as JSON (`.npy`), HTML (standalone page), or PDF (via `fpdf2`)
-  **CLI Converter** — Convert `.npy`/`.ngo` notebook files into a structured code project folder via `python app.py convert <file>`
-  **Collaborative Editing** — Real-time cell editing, adding, deleting, and reordering via Socket.IO rooms
-  **Auto-Save** — Saves the current project to the database every 30 seconds automatically
-  **Cell Drag-and-Drop Reorder** — Drag cells by their handle to reorder them
-  **Cell Search Filter** — Filter cells by their code content or language tag
-  **Dark/Light Theme Toggle** — Switch between dark and light themes; persists across sessions
-  **CodeMirror Editor Themes** — Choose from Palenight, Darcula, Monokai, Solarized, or Light for the editor
-  **Per-Cell Undo/Redo** — Global undo and redo across all cells
-  **Keyboard Shortcuts** — Ctrl+Enter to run, Ctrl+S to save, Ctrl+Shift+Enter run-and-advance, Ctrl+Shift+N new project
-  **System Status Monitor** — Live RAM, CPU, and disk usage displayed in the header and settings page
-  **Kernel Management** — Restart or cancel the Python kernel from both the editor and settings page
-  **Sidebar Collapse** — Toggle the sidebar for more horizontal editing space
-  **Secure Mode** — API key authentication for all requests (including WebSocket) with `python app.py start`
-  **Magic Commands** — Execute shell commands inline with `!command` syntax in Python cells
-  **Rate Limiting** — Flask-Limiter enforces 200 requests/minute and 20 requests/second
-  **Security Headers** — CSP, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
-  **Docker Support** — Ready-to-use Dockerfile and docker-compose.yml
-  **CI Testing** — GitHub Actions runs 27 unit tests across Python 3.10, 3.11, and 3.12
-  **Responsive Design** — Mobile-friendly layout with sidebar, FAB, and adaptive cells

---

## Quick Start

### Prerequisites

- Python 3.10 or later
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/anomalyco/nbook.git
cd nbook

# Install dependencies
pip install -r requirements.txt

# Run in free mode (no authentication required)
python app.py free
```

Open your browser to `http://127.0.0.1:52896` and start coding.

> **Free mode** is for local / trusted-network use. For production or exposed deployments, use **secure mode**:
> ```bash
> python app.py start
> ```
> This generates a unique API key printed to the console. Access the app via `http://127.0.0.1:52896?key=<api-key>`.

---

## Usage Guide

### Creating and Running Cells

1. Click **PY** (or the **+** button for HTML, Markdown, JS, Bash) to add a new cell.
2. Write your code in the CodeMirror editor.
3. Click **RUN** (or press `Ctrl+Enter`) to execute.
   - **Python** cells run in a shared stateful kernel. Variables persist across cells.
   - **Bash** cells run shell commands (no state).
   - **HTML** cells render the HTML in a preview area below the editor.
   - **Markdown** cells render GitHub-flavored markdown using `marked`.
   - **JavaScript** cells execute in the browser context; `console.log` output is captured.
4. The result (output text or rendered content) appears below the cell.
5. Matplotlib plots are automatically captured and displayed as inline images.

### File Management

The **FILES** tab in the sidebar lists all files in the workspace directory.

| Action    | How                                                                 |
|-----------|----------------------------------------------------------------------|
| Browse    | Click on folder names to navigate                                    |
| Go up     | Click the `..` back button                                           |
| New file  | Enter a name in the input field and click **+FILE**                  |
| New dir   | Enter a name and click **+DIR**                                      |
| Upload    | Click **UPLOAD** and select a file from your computer                |
| Download  | Hover over a file and click the download icon                        |
| Rename    | Hover over a file and click the pencil icon                          |
| Delete    | Hover over a file and click the trash icon                           |
| Edit      | Click a file name to open the in-browser text editor                 |
| Open cell | Click the link icon to load file contents into a new code cell       |

### Terminal Access

Switch to the **TERM** tab in the sidebar to access the integrated terminal.

- The terminal is backed by a PTY (Unix) or a subprocess (Windows) — `bash` on Unix, `powershell`/`cmd` on Windows.
- Input is sent via WebSocket, output is streamed in real time.
- The terminal automatically initializes when you switch to the TERM tab.

### Project History

Navigate to `/history` or click the clock icon in the sidebar header to open project history.

| Action | How                                                                |
|--------|----------------------------------------------------------------------|
| Save   | Click **SAVE PROJECT** in the sidebar (or press `Ctrl+S`)            |
| Load   | On the history page, click **OPEN** on any saved project             |
| Rename | Hover over a project title and click the pencil icon                 |
| Delete | Click the trash icon, confirm when prompted                          |
| Export | Click the download icon to export the project as `.npy` (JSON format)|

When you open a project from history, its cells are loaded into the editor and the project ID is tracked — subsequent saves update the same record.

### Settings Page

Navigate to `/settings` or click **SETTINGS** in the sidebar.

**System Status** — Live RAM and disk usage bars with a **RESTART KERNEL** button.

**Theme** — Toggle between dark and light mode globally.

**Editor Theme** — Select a CodeMirror theme: Palenight, Darcula, Monokai, Solarized, or Default (Light).

**Export Project** — Select a saved project from the dropdown and export as JSON, HTML, or PDF.

### Authentication

| Page       | Route             | Description                                                       |
|------------|-------------------|-------------------------------------------------------------------|
| Register   | `/auth/register`  | Create an account (username, password, optional name and email)    |
| Login      | `/auth/login`     | Sign in with username and password                                 |
| Profile    | `/auth/profile`   | Update full name, email, and password. View your username.         |
| Logout     | Click LOGOUT      | Clears the session and returns you to anonymous mode               |

Once logged in, your username appears in the sidebar and you remain authenticated for the session.

### Export Options

| Format | How to Export                                                                 |
|--------|-------------------------------------------------------------------------------|
| JSON   | Click **JSON** in the sidebar (exports all cells as `project.npy`)            |
| HTML   | Click **HTML** in the sidebar (downloads a standalone HTML page of all cells) |
| PDF    | Click **PDF** in the sidebar (generates a PDF via `fpdf2` on the server)      |
| CLI    | `python app.py convert project.npy` — converts to a `_project` code folder    |

### Collaborative Editing

N-BOOK supports real-time collaborative editing via Socket.IO rooms.

- When you open a project from history, you automatically join a room keyed to that project's ID.
- Any cell edits, additions, deletions, reorders, and title changes are broadcast to all other clients in the same room.
- Each collaborator sees changes in real time (with a 500 ms debounce on edits).
- To collaborate, simply share the project URL (with `load_id=<id>`). All users who load the same project collaborate in the same room.

### Keyboard Shortcuts

| Shortcut                   | Action                               |
|----------------------------|--------------------------------------|
| `Ctrl+Enter`               | Run the last cell                    |
| `Ctrl+Shift+Enter`         | Run the last cell and add a new one  |
| `Ctrl+S`                   | Save project                         |
| `Ctrl+Shift+N`             | New project (with confirmation)      |
| `Ctrl+Space` (in editor)   | CodeMirror autocomplete              |

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Client Browser                       │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │Notebook  │  │CodeMirror│  │ Xterm.js │  │File     │ │
│  │Container │  │Cells     │  │Terminal  │  │Explorer │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │              │             │              │      │
│       └──────────────┼─────────────┼──────────────┘      │
│                      │  WebSocket  │                    │
│                      └──────┬──────┘                    │
│                             │ HTTP                      │
└─────────────────────────────┼────────────────────────────┘
                              │
┌─────────────────────────────┼────────────────────────────┐
│                    Flask Server                          │
│  ┌──────────────────────────┴────────────────────────┐  │
│  │              Flask-SocketIO                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────────────┐ │  │
│  │  │ Terminal │ │Executor  │ │ Routes & Middleware │ │  │
│  │  │ (PTY)    │ │(Stateful │ │ (HTTP + WS)        │ │  │
│  │  └──────────┘ │ Python)  │ └────────┬───────────┘ │  │
│  │               └──────────┘          │              │  │
│  └──────────────────────────────────────┼──────────────┘  │
│                                         │                │
│  ┌──────────┐  ┌───────────┐  ┌────────┴────────┐      │
│  │ SQLite   │  │ Workspace │  │  psutil / Git   │      │
│  │ Database │  │ Directory │  │  / fpdf2        │      │
│  └──────────┘  └───────────┘  └─────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

**Backend modules:**
- `app.py` — Application factory, extension initialization, security headers, error handlers
- `config.py` — Configuration from environment variables / `.env`
- `core/__init__.py` — SQLAlchemy and SocketIO extension instances
- `core/cli.py` — Click CLI (`start`, `free`, `convert`)
- `core/executor.py` — Stateful Python execution with matplotlib patch, magic commands, cancellation
- `core/routes.py` — All HTTP routes and Socket.IO event handlers (file ops, history, system, terminal, export, git, collab)
- `core/auth.py` — Register, login, logout, profile management
- `core/models.py` — `User` and `Notebook` SQLAlchemy models
- `core/terminal.py` — Server startup in free/secure mode, notebook-to-project converter
- `core/utils.py` — `get_safe_path` helper for workspace path traversal prevention

**Database:**
- SQLite database at `data/nbook.db`
- `User` table: id, username, password_hash, full_name, email
- `Notebook` table: id, title, content (JSON-serialized cells), user_id (nullable)

**Security:**
- Free mode (no auth) vs. Secure mode (API key required for all requests)
- Path traversal prevention via `get_safe_path`
- File upload extension blacklist
- CSP, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection headers
- Flask-Limiter rate limiting
- Password hashing via Werkzeug

---

## Docker Deployment

### Using Docker Compose (recommended)

```bash
docker compose up -d
```

This builds the image, starts the container on port `52896`, and mounts `data/` and `workspace/` for persistence.

### Using Docker directly

```bash
docker build -t nbook .
docker run -d \
  --name nbook \
  -p 52896:52896 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/workspace:/app/workspace" \
  nbook
```

Access `http://localhost:52896` in your browser.

---

## Testing

27 unit tests covering the executor, routes, and terminal modules.

```bash
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_executor.py -v
python -m pytest tests/test_routes.py -v
python -m pytest tests/test_terminal.py -v
```

GitHub Actions CI runs the full test suite on every push/PR to `main` across Python 3.10, 3.11, and 3.12.

**Test coverage:**
- **Executor (18 tests):** simple print, eval expressions, variable persistence, syntax/runtime errors, magic commands, cancellation, variable inspection (including private variable exclusion), matplotlib injection, kernel restart clears globals
- **Routes (12 tests):** home page, system stats, empty variables, file listing, history page, 404 handler, kernel restart/cancel, save and load notebook, save file and read, create and delete file, secure mode blocks, secure mode with valid key
- **Terminal (3 tests):** file not found, invalid JSON, valid notebook conversion to project folder

---

## Configuration

All configuration is managed via environment variables or a `.env` file (copy `.env.example` to `.env`).

| Variable       | Default              | Description                                  |
|----------------|----------------------|----------------------------------------------|
| `SECRET_KEY`   | `nbook-secret-key`   | Flask session signing key                    |
| `NBOOK_PORT`   | `52896`              | Server port                                  |
| `NBOOK_MODE`   | `free`               | `free` (no auth) or `secure` (API key needed)|

Additional hardcoded config:
- Max upload size: 50 MB
- Rate limiting: 200 requests/minute, 20 requests/second
- Database: SQLite at `data/nbook.db`
- Workspace directory: `workspace/`

---

## API Endpoints

### Pages
| Method | Path              | Description                       |
|--------|-------------------|-----------------------------------|
| GET    | `/`               | Main editor page                  |
| GET    | `/history`        | Project history page              |
| GET    | `/settings`       | Settings page                     |
| GET    | `/auth/login`     | Login page                        |
| GET    | `/auth/register`  | Registration page                 |
| GET    | `/auth/profile`   | Profile page                      |

### API
| Method | Path                  | Description                         |
|--------|-----------------------|-------------------------------------|
| POST   | `/save`               | Save notebook to database           |
| GET    | `/system/stats`       | CPU, RAM, and disk usage            |
| POST   | `/system/restart`     | Restart kernel and clear globals    |
| POST   | `/kernel/restart`     | Restart kernel                      |
| POST   | `/kernel/cancel`      | Cancel running execution            |
| GET    | `/variables`          | List all non-private Python globals |
| GET    | `/git/clone`          | Clone a Git repository              |
| POST   | `/export/html`        | Export cells as HTML                |
| POST   | `/export/pdf`         | Export cells as PDF                 |
| POST   | `/files/upload`       | Upload a file                       |
| POST   | `/files/delete`       | Delete a file or directory          |
| POST   | `/files/rename`       | Rename a file                       |
| POST   | `/files/create`       | Create a file or directory          |
| GET    | `/files/list`         | List directory contents             |
| GET    | `/files/read`         | Read file contents                  |
| GET    | `/files/download`     | Download a file                     |
| POST   | `/save-file`          | Save content to a file              |
| POST   | `/history/delete/<id>`| Delete a saved project              |
| POST   | `/history/rename/<id>`| Rename a saved project              |
| GET    | `/history/load/<id>`  | Load a saved project                |
| GET    | `/history/export/<id>`| Export a saved project as `.npy`    |

### Auth
| Method | Path                | Description                          |
|--------|---------------------|--------------------------------------|
| POST   | `/auth/register`    | Register a new user                  |
| POST   | `/auth/login`       | Log in                               |
| POST   | `/auth/logout`      | Log out                              |
| GET    | `/auth/me`          | Get current authenticated user info  |
| POST   | `/auth/profile`     | Update profile                       |

### Socket.IO Events
| Event             | Direction       | Description                           |
|-------------------|-----------------|---------------------------------------|
| `execute_code`    | Client→Server   | Request code execution                |
| `execution_result`| Server→Client   | Code execution result (output/plots)  |
| `terminal_input`  | Client→Server   | Send terminal keystroke               |
| `terminal_output` | Server→Client   | Receive terminal output               |
| `join_notebook`   | Client→Server   | Join a collaborative editing room     |
| `leave_notebook`  | Client→Server   | Leave a collaborative editing room    |
| `cell_edit`       | Bidirectional   | Collaborative cell content edit       |
| `cell_add`        | Bidirectional   | Collaborative cell add                |
| `cell_delete`     | Bidirectional   | Collaborative cell delete             |
| `cell_reorder`    | Bidirectional   | Collaborative cell reorder            |
| `nb_title`        | Bidirectional   | Collaborative notebook title change   |

---

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in free mode with debug
python app.py free

# Run tests
python -m pytest tests/ -v

# Convert a notebook to a project folder
python app.py convert my_notebook.npy
```

### Project Structure

```
nbook/
├── app.py                  # Application factory
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose
├── .env.example            # Environment config template
├── core/
│   ├── __init__.py         # Extensions (db, socketio)
│   ├── auth.py             # Authentication routes
│   ├── cli.py              # CLI commands
│   ├── executor.py         # Stateful Python executor
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # HTTP routes & SocketIO events
│   ├── terminal.py         # Server modes & converter
│   └── utils.py            # Utility functions
├── tests/
│   ├── test_executor.py    # 18 tests
│   ├── test_routes.py      # 12 tests
│   └── test_terminal.py    # 3 tests
├── templates/              # Jinja2 templates
│   ├── base.html           # Base layout (Tailwind, CodeMirror, etc.)
│   ├── index.html          # Main editor (cells, sidebar, terminal)
│   ├── history.html        # Project history page
│   ├── settings.html       # Settings page
│   ├── profile.html        # User profile page
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   └── error.html          # 404/403/500 error page
├── static/
│   └── images/logo.svg     # App logo
├── data/                   # SQLite database (created at runtime)
├── workspace/              # User file workspace (created at runtime)
├── docs/
│   ├── ARCHITECTURE.md     # Architecture documentation
│   └── CONFIGURATION.md    # Configuration guide
└── .github/workflows/      # CI configuration
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run the tests (`python -m pytest tests/ -v`)
5. Commit with a descriptive message
6. Push and open a pull request

Please ensure your code follows the existing style conventions (no comments, consistent indentation, meaningful names).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

Copyright (c) 2025 RK RIAD 585 (RK STUDIO 585)
