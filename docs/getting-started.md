# Getting Started with Nbook

Nbook is a web-based interactive notebook environment. It lets you write and run Python code, render HTML and Markdown, execute JavaScript and Bash commands -- all from your browser. It includes a built-in terminal, file explorer, Git integration, real-time system monitoring, and collaborative editing.

This guide walks you through everything you need to go from zero to productive.

---

## 1. Prerequisites

Before you begin, make sure your system has:

- **Python 3.10 or higher** -- Nbook requires Python 3.10+. Check your version:

  ```bash
  python --version
  ```

  If you see `Python 3.10.x` or higher, you are good. On Windows, `python` may be `py` or `python3`.

- **pip** -- Python's package installer (ships with Python 3.10+).

- **Git** (optional) -- Needed if you want to clone repositories from within Nbook.

- A modern web browser -- Chrome, Firefox, or Edge recommended.

---

## 2. Installation

### 2.1 Clone the repository

```bash
git clone https://github.com/rkriad585/Nbook.git
cd Nbook
```

If you do not have Git, download the source ZIP from GitHub and extract it, then `cd` into the extracted folder.

### 2.2 Create a virtual environment (recommended)

Using a virtual environment keeps Nbook's dependencies isolated from other Python projects.

**Windows (Command Prompt):**

```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### 2.3 Install dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:

| Package            | Purpose                               |
|--------------------|---------------------------------------|
| Flask              | Web framework                         |
| Flask-SQLAlchemy   | Database ORM (SQLite)                 |
| Flask-SocketIO     | Real-time WebSocket communication     |
| Flask-Limiter      | Rate limiting for API endpoints       |
| Click              | CLI command interface                 |
| psutil             | System monitoring (CPU, RAM, disk)    |
| GitPython          | Git repository cloning                |
| python-socketio    | WebSocket client (for tests)          |
| python-dotenv      | Environment variable loading          |
| matplotlib         | Plotting support in Python cells      |
| fpdf2              | PDF export                            |

---

## 3. First Run

Nbook has two modes: **free** (no authentication) and **secure** (with API key protection).

### 3.1 Free mode

```bash
python app.py free
```

You will see output like:

```
[FREE MODE] http://127.0.0.1:52896
```

Open `http://127.0.0.1:52896` in your browser. That is it -- you are in.

### 3.2 Secure mode

```bash
python app.py start
```

The console prints a URL with a generated API key:

```
[SECURE MODE] http://127.0.0.1:52896?key=5c8a3f1e-...
```

You **must** use that exact URL (with the `?key=...` parameter) to access Nbook. Without the key, the server returns a 403 error.

### 3.3 Custom port

Set the `NBOOK_PORT` environment variable to change the port:

```bash
# Windows (PowerShell)
$env:NBOOK_PORT=8080
python app.py free

# Linux / macOS
export NBOOK_PORT=8080
python app.py free
```

### 3.4 Environment file

Copy `.env.example` to `.env` and edit it:

```bash
cp .env.example .env
```

Supported variables:

```env
SECRET_KEY=your-random-secret-key
NBOOK_PORT=52896
NBOOK_MODE=free
```

---

## 4. Creating Your First Notebook

When Nbook loads, you are greeted with a dark-themed editor. A single empty Python cell is already waiting for you.

The main interface is split into:

- **Sidebar (left)** -- File explorer, terminal, variables pane, and Git tools. Collapse it with the arrow button at the top.
- **Main area (center)** -- Your notebook cells. The title is editable at the top.
- **Header (top)** -- RAM/Disk meters, connection status, undo/redo, kernel restart, and the **PY** / **+** buttons for adding cells.

To start, click the title "Untitled Research" and rename it to something like "My First Notebook".

---

## 5. Adding Cells

Nbook supports five cell types. Click the **PY** button to add a Python cell, or click the **+** button to see the other types.

| Cell Type   | Badge Color | What It Does                                  |
|-------------|-------------|-----------------------------------------------|
| Python      | Blue        | Executes Python code with stateful variables  |
| HTML        | Orange      | Renders HTML directly in the cell preview     |
| Markdown    | Purple      | Renders Markdown as formatted text            |
| JavaScript  | Yellow      | Runs JavaScript in the browser (client-side)  |
| Bash        | Green       | Runs shell commands on the server             |

Each cell has a **RUN** (or **PREVIEW**) button, an undo button, and a delete (X) button. Cells are draggable via the grip icon in the top-left corner.

### Keyboard shortcuts

| Shortcut              | Action                          |
|-----------------------|---------------------------------|
| `Ctrl + Enter`        | Run the last cell               |
| `Ctrl + Shift + Enter`| Run the last cell and add a new one |
| `Ctrl + S`            | Save the project                |
| `Ctrl + Shift + N`    | New project                     |

---

## 6. Running Code

### Python cells

Every Python cell shares a single global namespace (`PYTHON_GLOBALS`). Variables defined in one cell are available in all subsequent cells:

```python
# Cell 1
x = 42
message = "Hello from Nbook"
```

```python
# Cell 2
print(message)  # Output: Hello from Nbook
print(x * 2)    # Output: 84
```

The output of each cell (anything printed to stdout) appears in the result area below the editor.

### Matplotlib plotting

Matplotlib is supported out of the box. When you call `plt.show()`, the plot is captured as an inline PNG image:

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title("Sine Wave")
plt.show()
```

The plot renders directly in the cell's result area.

### Shell magic commands

Prefix a line with `!` to run a shell command:

```python
!ls -la
!echo "Hello from the shell"
```

The command runs on the server and its output is captured.

### HTML cells

Write any HTML and click **PREVIEW** to render it:

```html
<h1 style="color: cyan;">Hello World</h1>
<p>This is rendered inline.</p>
```

### Markdown cells

Write Markdown and click **PREVIEW**:

```markdown
# Heading

- List item 1
- List item 2

**Bold text** and *italic text*.
```

The Markdown is rendered using the `marked` library directly in your browser.

### JavaScript cells

Write JavaScript that runs in the browser:

```javascript
const greeting = "Hello from JS";
console.log(greeting);
document.body.style.backgroundColor = "#111";
```

The cell captures `console.log`, `console.warn`, and `console.error` output.

### Bash cells

Run shell commands on the server:

```bash
echo "Current directory: $(pwd)"
ls -la
df -h
```

---

## 7. Saving and Loading Projects

### Save

Click **SAVE PROJECT** in the sidebar (or press `Ctrl+S`). The project is saved to the SQLite database (`data/nbook.db`). Nbook also auto-saves every 30 seconds.

A project ID is assigned on first save. Subsequent saves update the same record.

### Load from history

Click the clock icon in the sidebar header, or navigate to `/history`. You will see a list of saved projects. Each entry shows:

- **Project title** -- Click the pencil icon to rename it.
- **OPEN** -- Loads the project into the editor (appends `?load_id=<id>` to the URL).
- **Export icon** -- Downloads the project as a `.npy` JSON file.
- **Trash icon** -- Permanently deletes the project.

### New project

Click the **+** icon (document with a star) in the sidebar header, or press `Ctrl+Shift+N`. Confirm when prompted -- unsaved changes are lost.

### Sharing projects via URL

You can share a load link directly:

```
http://127.0.0.1:52896/?load_id=5
```

In secure mode, append the API key:

```
http://127.0.0.1:52896/?key=YOUR_KEY&load_id=5
```

---

## 8. File Management Basics

The **FILES** tab in the sidebar gives you a full file explorer rooted at the `workspace/` directory.

### Common operations

| Action                | How                                            |
|-----------------------|-------------------------------------------------|
| Browse directories    | Click a folder name                            |
| Go up                 | Click the `..` button                          |
| Create a file         | Type a name in the input box, click **+FILE**  |
| Create a folder       | Type a name, click **+DIR**                    |
| Upload a file         | Click **UPLOAD** and select a file             |
| Open in cell          | Click the link icon on a file                  |
| Edit in modal         | Click the file name                            |
| Download              | Click the download icon                        |
| Rename                | Click the pencil icon                          |
| Delete                | Click the trash icon                           |

### Editing files

Click any file name to open the in-browser file editor. It shows a modal with a text area. Edit the content and click **SAVE**.

### Opening files as cells

Click the link icon on a file to load its contents into a new cell. Nbook auto-detects the language from the file extension (`.py` -> Python, `.html` -> HTML, `.md` -> Markdown, `.js` -> JavaScript, `.sh` -> Bash).

### File type restrictions

Executable uploads (`.exe`, `.bat`, `.cmd`, `.sh`, `.ps1`, `.dll`, `.so`, etc.) are blocked for security.

---

## 9. Terminal Basics

The **TERM** tab in the sidebar provides a full terminal connected to the server.

### How it works

- On Linux/macOS: Nbook spawns a pseudo-terminal (`pty`) running `bash`.
- On Windows: Nbook spawns `powershell.exe` or `cmd.exe` as a subprocess.

### Using the terminal

1. Switch to the **TERM** tab in the sidebar.
2. The terminal starts automatically when you first open the tab.
3. Type commands and they execute on the server in real time.

Example commands you can run:

```bash
whoami
pwd
ls -la
pip list
python --version
```

The terminal uses [Xterm.js](https://xtermjs.org/) for rendering, with support for colors, cursor blinking, and terminal resize via the fit addon.

### Notes

- There is one shared terminal for all users in free mode.
- The terminal working directory is the `workspace/` folder.
- On Windows, shell commands run through a subprocess pipe rather than a PTY.

---

## 10. Saving and Loading Projects

### Save to database

```python
# Using the sidebar button or Ctrl+S
```

Projects are stored as JSON in the `Notebook` database table. Each cell stores its `language` and `code`.

### Download as JSON (.npy)

Click the **JSON** button in the sidebar (under "SAVE PROJECT"). This downloads all cells as a structured JSON file. You can re-import it by loading from history or using the CLI convert command.

### Export as HTML

Click the **HTML** button in the sidebar. This generates a standalone HTML document with embedded CSS and all cell content rendered as code blocks (Markdown and HTML cells are rendered inline).

### Export as PDF

Click the **PDF** button in the sidebar. This uses `fpdf2` to generate a monospace-formatted PDF with labeled cells and a title page.

### Export from Settings page

Navigate to `/settings` (or click **SETTINGS** in the sidebar). Select a saved project from the dropdown and choose JSON, HTML, or PDF export.

### CLI convert

Convert a `.npy` or `.ngo` project file to a folder of source files:

```bash
python app.py convert my_project.npy
```

This creates a `my_project_project/` folder containing `main.py` (all Python cells concatenated), plus `.html` and `.md` files for HTML and Markdown cells.

---

## 11. Settings Page Walkthrough

Navigate to `/settings` or click **SETTINGS** in the sidebar sidebar navigation row.

### System Status

Shows real-time RAM and disk usage bars (polled every 5 seconds). The **RESTART KERNEL** button clears all Python global variables and resets the execution state.

### Theme

Toggle between **DARK** and **LIGHT** mode. The setting is saved in `localStorage` and persists across sessions.

### Editor Theme

Choose a CodeMirror syntax highlighting theme:

| Theme               | Description             |
|---------------------|-------------------------|
| Palenight (Dark)    | Purple-based dark theme |
| Darcula             | JetBrains-style dark    |
| Monokai             | Classic dark theme      |
| Solarized           | Warm dark theme         |
| Light (Default)     | Light mode theme        |

### Export Project

Select any previously saved project from the dropdown and export it as JSON, HTML, or PDF -- useful for batch exporting or generating final deliverables.

### Navigation

Quick links to **EDITOR** (back to `/`) and **PROFILE** (user profile page).

---

## 12. Authentication Setup

Nbook includes a built-in user authentication system. Even in free mode, you can register accounts for personalized sessions.

### Registration

Navigate to `/auth/register` (or click **REGISTER** in the sidebar). Fill in:

- **Full Name** (optional)
- **Email** (optional)
- **Username** (required, must be unique)
- **Password** (required, minimum 4 characters)
- **Confirm Password**

On success, you are automatically logged in and redirected to the editor.

### Login

Navigate to `/auth/login` (or click **LOGIN** in the sidebar). Enter your username and password.

Once logged in, the sidebar shows your username and a **LOGOUT** button.

### Profile

Navigate to `/auth/profile` (or click **PROFILE** in the sidebar). You can:

- View your username (read-only)
- Update your full name and email
- Change your password (leave blank to keep current)

### How session management works

Authentication uses Flask's signed session cookies (`SESSION_COOKIE_SAMESITE='Lax'`, `SESSION_COOKIE_HTTPONLY=True`). The session stores `user_id` and `username`. The `/auth/me` endpoint returns the current user state and is polled by the frontend on page load.

### Secure mode vs authentication

These are separate systems:

- **Secure mode** (`python app.py start`) -- Protects the entire server with an API key. Every request must include `?key=...` or `X-API-KEY` header.
- **Authentication** -- Works in both free and secure modes. Lets users log in and manage profiles within an already-accessible instance.

---

## 13. Docker Deployment

Nbook includes a `Dockerfile` and `docker-compose.yml` for containerized deployment.

### Dockerfile

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

### Build and run with Docker

```bash
# Build the image
docker build -t nbook .

# Run the container
docker run -d \
  --name nbook \
  -p 52896:52896 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/workspace:/app/workspace" \
  nbook
```

### Run with docker-compose

```bash
docker-compose up -d
```

The `docker-compose.yml` mounts three volumes:

| Host path       | Container path    | Purpose                |
|-----------------|-------------------|------------------------|
| `./data`        | `/app/data`       | SQLite database        |
| `./workspace`   | `/app/workspace`  | User files             |
| `./.env`        | `/app/.env:ro`    | Environment (readonly) |

The default mode in Docker is `free`. Change the `NBOOK_MODE` environment variable in `docker-compose.yml` to `secure` if needed.

---

## 14. Troubleshooting Common Issues

### "flask is not recognized" / "ModuleNotFoundError"

Your virtual environment is not activated or dependencies are not installed.

```bash
# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Port already in use

```bash
# Change the port
$env:NBOOK_PORT=8080  # PowerShell
python app.py free
```

Or kill the process using the port:

```bash
# Windows
netstat -ano | findstr :52896
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :52896
kill -9 <PID>
```

### "data/nbook.db" does not exist

Nbook creates the `data/` directory and the SQLite database automatically on first run. If you deleted it, just restart the server -- it will be recreated.

### 403 Forbidden in secure mode

You are accessing without the API key. Use the exact URL printed when you ran `python app.py start`. It looks like:

```
http://127.0.0.1:52896?key=5c8a3f1e-...
```

You can also pass the key as an HTTP header: `X-API-KEY: 5c8a3f1e-...`.

### Code execution returns nothing

- Check if the cell type is Python or Bash (only those produce server-side output).
- Open the browser's developer console (`F12`) and look for WebSocket errors.
- Make sure the kernel has not been cleared. Click **RESTART** in the header to reset the Python globals.

### Terminal shows nothing

- On Windows, the terminal uses a subprocess pipe (no PTY). Some interactive programs may not work in this mode.
- Resize the sidebar or refresh the page to reinitialize Xterm.js.
- Only one terminal exists per server. If a previous connection left it in a bad state, restart the server.

### "File not found" errors in the file explorer

File operations are restricted to the `workspace/` directory. You cannot browse or access files outside this directory. Check that the file exists under `workspace/`.

### PDF export contains garbled characters

The `fpdf2` library only supports Latin-1 characters. Non-Latin characters (CJK, emoji, etc.) are replaced with a fallback character. For full Unicode support, consider exporting to HTML instead.

### Docker container exits immediately

Check the logs:

```bash
docker logs nbook
```

Common causes: missing `.env` file, port conflict on the host, or permission issues with mounted volumes.

### "Address already in use" on Docker

The host port `52896` is already taken. Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8080:52896"
```
