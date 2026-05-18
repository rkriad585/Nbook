# Nbook API Reference

Base URL: `http://localhost:5000` (default)

All routes (except `/static` and `/socket.io`) are subject to API key validation when the server runs in `secure` mode. Pass the key as a query parameter `?key=` or in the `X-API-KEY` header.

---

## Table of Contents

1. [Auth Endpoints](#1-auth-endpoints)
2. [Main Editor](#2-main-editor)
3. [System Endpoints](#3-system-endpoints)
4. [File Management Endpoints](#4-file-management-endpoints)
5. [Kernel Endpoints](#5-kernel-endpoints)
6. [Project / Notebook Endpoints](#6-project--notebook-endpoints)
7. [Git Endpoints](#7-git-endpoints)
8. [Export Endpoints](#8-export-endpoints)
9. [Settings](#9-settings)
10. [Socket.IO Events](#10-socketio-events)

---

## 1. Auth Endpoints

All auth routes are prefixed with `/auth`.

### 1.1 GET /auth/register

Render the registration form.

**Request:** No parameters.

**Response:** HTML page (`register.html`).

**Status codes:** `200 OK`

**Example:**
```
GET /auth/register
```

---

### 1.2 POST /auth/register

Create a new user account.

**Request body** (JSON or form-data):

| Field            | Type   | Required | Description            |
|------------------|--------|----------|------------------------|
| `username`       | string | Yes      | Unique username        |
| `password`       | string | Yes      | Min 4 characters       |
| `confirm_password` | string | Yes    | Must match password    |
| `full_name`      | string | No       | Display name           |
| `email`          | string | No       | Unique email address   |

**Response (201):**
```json
{
  "status": "registered",
  "username": "alice"
}
```

**Error responses:**
```json
// 400 - Validation error
{ "error": "Username and password required" }
{ "error": "Passwords do not match" }
{ "error": "Password must be at least 4 characters" }
{ "error": "Username already taken" }
{ "error": "Email already taken" }
```

**Status codes:** `201 Created`, `400 Bad Request`

**Example:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret","confirm_password":"secret","full_name":"Alice","email":"alice@example.com"}'
```

---

### 1.3 GET /auth/login

Render the login form.

**Request:** No parameters.

**Response:** HTML page (`login.html`).

**Status codes:** `200 OK`

---

### 1.4 POST /auth/login

Authenticate and create a session.

**Request body** (JSON or form-data):

| Field      | Type   | Required | Description  |
|------------|--------|----------|--------------|
| `username` | string | Yes      | User's username |
| `password` | string | Yes      | User's password |

**Response (200):**
```json
{
  "status": "logged_in",
  "username": "alice"
}
```

**Error responses:**
```json
// 401 - Invalid credentials
{ "error": "Invalid username or password" }
```

**Status codes:** `200 OK`, `401 Unauthorized`

**Example:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}'
```

---

### 1.5 POST /auth/logout

Clear the current session.

**Request:** No body required.

**Response (200):**
```json
{
  "status": "logged_out"
}
```

**Status codes:** `200 OK`

**Example:**
```bash
curl -X POST http://localhost:5000/auth/logout
```

---

### 1.6 GET /auth/me

Check the current authentication status.

**Request:** No parameters. Uses session cookie.

**Response (200) — authenticated:**
```json
{
  "authenticated": true,
  "username": "alice",
  "full_name": "Alice",
  "email": "alice@example.com"
}
```

**Response (200) — unauthenticated:**
```json
{
  "authenticated": false
}
```

**Status codes:** `200 OK`

**Example:**
```bash
curl http://localhost:5000/auth/me
```

---

### 1.7 GET /auth/profile

Render the profile page for the authenticated user. Redirects to `/auth/login` if not authenticated.

**Request:** Uses session cookie.

**Response:** HTML page (`profile.html`).

**Status codes:** `200 OK`, `302 Redirect` (if not authenticated)

---

### 1.8 POST /auth/profile

Update the authenticated user's profile.

**Request body** (JSON or form-data):

| Field             | Type   | Required | Description               |
|-------------------|--------|----------|---------------------------|
| `full_name`       | string | No       | New display name          |
| `email`           | string | No       | New email address         |
| `password`        | string | No       | New password (min 4 chars) |
| `confirm_password` | string | No      | Must match new password   |

**Response (200):**
```json
{
  "status": "updated",
  "user": {
    "username": "alice",
    "full_name": "Alice Smith",
    "email": "alice@newdomain.com"
  }
}
```

**Error responses:**
```json
// 400 - Validation error
{ "error": "Passwords do not match" }
{ "error": "Password must be at least 4 characters" }

// 401 - Not authenticated
{ "error": "Not authenticated" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `401 Unauthorized`, `404 Not Found`

**Example:**
```bash
curl -X POST http://localhost:5000/auth/profile \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Alice Smith","email":"alice@newdomain.com"}'
```

---

## 2. Main Editor

### 2.1 GET /

Render the main notebook editor page.

**Request:** No parameters.

**Response:** HTML page (`index.html`).

**Status codes:** `200 OK`

**Example:**
```
GET /
```

---

## 3. System Endpoints

### 3.1 GET /system/stats

Return live CPU, RAM, and disk usage statistics.

**Request:** No parameters.

**Response (200):**
```json
{
  "status": "online",
  "cpu": 23.5,
  "ram": {
    "percent": 67.2,
    "used": 12.45,
    "total": 16.0
  },
  "disk": {
    "percent": 45.0,
    "used": 224.8,
    "total": 500.0
  }
}
```

If stats cannot be read, numeric fields default to `0` or `0.0`.

**Status codes:** `200 OK`

**Example:**
```bash
curl http://localhost:5000/system/stats
```

---

### 3.2 POST /system/restart

Restart the kernel by clearing all Python globals and cancelling execution.

**Request:** No body required.

**Response (200):**
```json
{
  "status": "restarted"
}
```

**Status codes:** `200 OK`

**Example:**
```bash
curl -X POST http://localhost:5000/system/restart
```

---

## 4. File Management Endpoints

All file routes use `get_safe_path()` to ensure path traversal is blocked — only files under the configured `WORKSPACE` directory are accessible.

### 4.1 GET /files/list?path=

List files and directories in the specified workspace path.

**Query parameters:**

| Parameter | Type   | Required | Default | Description                |
|-----------|--------|----------|---------|----------------------------|
| `path`    | string | No       | `""`    | Relative workspace subpath |

**Response (200):**
```json
[
  {
    "name": "src",
    "path": "src",
    "is_dir": true
  },
  {
    "name": "main.py",
    "path": "main.py",
    "is_dir": false
  }
]
```

Hidden files (starting with `.`) are excluded. Results are sorted by directories first, then alphabetically.

**Error responses:**
```json
// 400 - Invalid directory
{ "error": "Invalid directory" }
```

**Status codes:** `200 OK`, `400 Bad Request`

**Example:**
```bash
curl "http://localhost:5000/files/list?path=src"
```

---

### 4.2 GET /files/read?path=

Read the contents of a text file.

**Query parameters:**

| Parameter | Type   | Required | Description                |
|-----------|--------|----------|----------------------------|
| `path`    | string | Yes      | Relative path to the file  |

**Response (200):**
```json
{
  "content": "print('hello')\n"
}
```

Binary files (non-text MIME types) are rejected.

**Error responses:**
```json
// 404 - File not found
{ "error": "File not found" }

// 400 - Binary file
{ "error": "Binary file preview not supported" }

// 500 - Read error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`

**Example:**
```bash
curl "http://localhost:5000/files/read?path=main.py"
```

---

### 4.3 POST /files/delete

Delete a file or directory.

**Request body:**

| Field  | Type   | Required | Description                    |
|--------|--------|----------|--------------------------------|
| `path` | string | Yes      | Relative path to the file/dir  |

**Response (200):**
```json
{
  "status": "success"
}
```

Directories are removed recursively.

**Error responses:**
```json
// 400 - Invalid path
{ "error": "Invalid path" }

// 500 - Deletion error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

**Example:**
```bash
curl -X POST http://localhost:5000/files/delete \
  -H "Content-Type: application/json" \
  -d '{"path":"old_script.py"}'
```

---

### 4.4 POST /files/rename

Rename a file or directory.

**Request body:**

| Field     | Type   | Required | Description                 |
|-----------|--------|----------|-----------------------------|
| `old_path`| string | Yes      | Current relative path       |
| `new_name`| string | Yes      | New name (not full path)    |

**Response (200):**
```json
{
  "status": "success"
}
```

**Error responses:**
```json
// 404 - File not found
{ "error": "File not found" }

// 400 - Name already exists / Invalid path
{ "error": "Name already exists" }
{ "error": "Invalid path" }

// 500 - Rename error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`

**Example:**
```bash
curl -X POST http://localhost:5000/files/rename \
  -H "Content-Type: application/json" \
  -d '{"old_path":"old.py","new_name":"new.py"}'
```

---

### 4.5 POST /save-file

Save content to a file (overwrite).

**Request body:**

| Field     | Type   | Required | Description              |
|-----------|--------|----------|--------------------------|
| `path`    | string | Yes      | Relative file path       |
| `content` | string | Yes      | File content to write    |

**Response (200):**
```json
{
  "status": "success"
}
```

**Error responses:**
```json
// 400 - Invalid path
{ "error": "Invalid path" }

// 500 - Write error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

**Example:**
```bash
curl -X POST http://localhost:5000/save-file \
  -H "Content-Type: application/json" \
  -d '{"path":"notebook.py","content":"print('hello world')"}'
```

---

### 4.6 POST /files/upload

Upload a file (multipart form data).

**Request:** `multipart/form-data`

| Field    | Type   | Required | Description                          |
|----------|--------|----------|--------------------------------------|
| `file`   | File   | Yes      | The file to upload                   |
| `path`   | string | No       | Destination directory (relative)     |

Blocked file extensions: `.exe`, `.bat`, `.cmd`, `.com`, `.msi`, `.scr`, `.pif`, `.sh`, `.pyc`, `.dll`, `.so`, `.dylib`, `.vbs`, `.ps1`, `.app`.

**Response (200):**
```json
{
  "status": "success",
  "path": "uploads/photo.jpg"
}
```

**Error responses:**
```json
// 400 - No file / Type not allowed / Invalid directory
{ "error": "No file provided" }
{ "error": "File type not allowed" }
{ "error": "Invalid directory" }

// 500 - Upload error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

**Example:**
```bash
curl -X POST http://localhost:5000/files/upload \
  -F "file=@photo.jpg" \
  -F "path=uploads"
```

---

### 4.7 GET /files/download?path=

Download a file as a binary attachment.

**Query parameters:**

| Parameter | Type   | Required | Description               |
|-----------|--------|----------|---------------------------|
| `path`    | string | Yes      | Relative path to file     |

**Response:** Binary file download with `Content-Disposition: attachment` header.

**Error responses:**
```json
// 404 - File not found
{ "error": "File not found" }

// 500 - Download error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `404 Not Found`, `500 Internal Server Error`

**Example:**
```bash
curl -O http://localhost:5000/files/download?path=data.csv
```

---

### 4.8 POST /files/create

Create an empty file or directory.

**Request body:**

| Field  | Type   | Required | Default    | Description                     |
|--------|--------|----------|------------|---------------------------------|
| `path` | string | Yes      | —          | Relative path for the new entry |
| `type` | string | No       | `"file"`   | `"file"` or `"directory"`       |

**Response (200):**
```json
{
  "status": "success"
}
```

**Error responses:**
```json
// 400 - Invalid path / Already exists
{ "error": "Invalid path" }
{ "error": "Already exists" }

// 500 - Creation error
{ "error": "<error message>" }
```

**Status codes:** `200 OK`, `400 Bad Request`, `500 Internal Server Error`

**Example:**
```bash
# Create a file
curl -X POST http://localhost:5000/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"new_file.py","type":"file"}'

# Create a directory
curl -X POST http://localhost:5000/files/create \
  -H "Content-Type: application/json" \
  -d '{"path":"new_folder","type":"directory"}'
```

---

## 5. Kernel Endpoints

### 5.1 GET /variables

Return Python variables currently stored in the kernel's global scope.

**Request:** No parameters.

**Response (200):**
```json
[
  {"name": "x", "type": "int", "value": "42"},
  {"name": "data", "type": "list", "value": "[...]"},
  {"name": "df", "type": "DataFrame", "value": "Shape: (100, 5)"}
]
```

The exact format depends on the `get_variables()` implementation in `core/executor.py`.

**Status codes:** `200 OK`

**Example:**
```bash
curl http://localhost:5000/variables
```

---

### 5.2 POST /kernel/restart

Clear all Python globals from the kernel state.

**Request:** No body required.

**Response (200):**
```json
{
  "status": "restarted"
}
```

**Status codes:** `200 OK`

**Example:**
```bash
curl -X POST http://localhost:5000/kernel/restart
```

---

### 5.3 POST /kernel/cancel

Cancel the currently executing Python code.

**Request:** No body required.

**Response (200):**
```json
{
  "status": "cancelled"
}
```

**Status codes:** `200 OK`

**Example:**
```bash
curl -X POST http://localhost:5000/kernel/cancel
```

---

## 6. Project / Notebook Endpoints

### 6.1 POST /save

Save or update a notebook project.

**Request body:**

| Field   | Type   | Required | Default      | Description                     |
|---------|--------|----------|--------------|---------------------------------|
| `title` | string | No       | `"Untitled"` | Notebook title                  |
| `cells` | array  | Yes      | —            | Array of cell objects           |
| `id`    | int    | No       | `null`       | Existing project ID (for update)|

Each cell object typically contains `language`, `code`, and `id` fields.

**Response (200) — new save:**
```json
{
  "status": "saved",
  "id": 1
}
```

**Response (200) — update:**
```json
{
  "status": "updated",
  "id": 1
}
```

**Status codes:** `200 OK`

**Example:**
```bash
curl -X POST http://localhost:5000/save \
  -H "Content-Type: application/json" \
  -d '{"title":"My Notebook","cells":[{"language":"python","code":"print(1)","id":"cell-1"}]}'
```

**Update existing:**
```bash
curl -X POST http://localhost:5000/save \
  -H "Content-Type: application/json" \
  -d '{"id":1,"title":"My Notebook","cells":[]}'
```

---

### 6.2 GET /history

Render the project history page.

**Request:** No parameters.

**Response:** HTML page (`history.html`) with all notebooks listed.

**Status codes:** `200 OK`

---

### 6.3 GET /history/load/{id}

Load a saved notebook by its ID.

**Path parameters:**

| Parameter | Type | Description    |
|-----------|------|----------------|
| `id`      | int  | Notebook ID    |

**Response (200):**
```json
{
  "id": 1,
  "title": "My Notebook",
  "cells": [
    {"language": "python", "code": "print(1)", "id": "cell-1"}
  ]
}
```

**Error responses:**
```json
// 404 - Not found
{ "error": "Not Found" }
```

**Status codes:** `200 OK`, `404 Not Found`

**Example:**
```bash
curl http://localhost:5000/history/load/1
```

---

### 6.4 POST /history/delete/{id}

Delete a saved notebook.

**Path parameters:**

| Parameter | Type | Description    |
|-----------|------|----------------|
| `id`      | int  | Notebook ID    |

**Request:** No body required.

**Response (200):**
```json
{
  "status": "success"
}
```

**Error responses:**
```json
// 404 - Not found
```

**Status codes:** `200 OK`, `404 Not Found`

**Example:**
```bash
curl -X POST http://localhost:5000/history/delete/1
```

---

### 6.5 POST /history/rename/{id}

Rename a saved notebook.

**Path parameters:**

| Parameter | Type | Description    |
|-----------|------|----------------|
| `id`      | int  | Notebook ID    |

**Request body:**

| Field   | Type   | Required | Description     |
|---------|--------|----------|-----------------|
| `title` | string | No       | New notebook title |

**Response (200):**
```json
{
  "status": "success",
  "title": "New Title"
}
```

**Status codes:** `200 OK`, `404 Not Found`

**Example:**
```bash
curl -X POST http://localhost:5000/history/rename/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Renamed Notebook"}'
```

---

### 6.6 GET /history/export/{id}

Download a saved notebook as a `.npy` file (JSON format).

**Path parameters:**

| Parameter | Type | Description    |
|-----------|------|----------------|
| `id`      | int  | Notebook ID    |

**Response:** File download (`application/json`) with `Content-Disposition: attachment; filename={title}.npy`.

```json
{
  "cells": [
    {"language": "python", "code": "print(1)", "id": "cell-1"}
  ]
}
```

**Status codes:** `200 OK`, `404 Not Found`

**Example:**
```bash
curl -O http://localhost:5000/history/export/1
```

---

## 7. Git Endpoints

### 7.1 POST /git/clone

Clone a Git repository into the workspace.

**Request body:**

| Field | Type   | Required | Description    |
|-------|--------|----------|----------------|
| `url` | string | Yes      | Git clone URL  |

**Response (200):**
```json
{
  "status": "success"
}
```

**Response (400):**
```json
{
  "status": "error",
  "message": "Repository not found"
}
```

**Status codes:** `200 OK`, `500 Internal Server Error`

**Example:**
```bash
curl -X POST http://localhost:5000/git/clone \
  -H "Content-Type: application/json" \
  -d '{"url":"https://github.com/user/repo.git"}'
```

---

## 8. Export Endpoints

### 8.1 POST /export/html

Export a notebook as an HTML file download.

**Request body:**

| Field   | Type   | Required | Default        | Description              |
|---------|--------|----------|----------------|--------------------------|
| `title` | string | No       | `"Notebook"`   | Document title           |
| `cells` | array  | Yes      | —              | Array of cell objects    |

Each cell object:
| Field      | Type   | Description                     |
|------------|--------|---------------------------------|
| `language` | string | `"python"`, `"markdown"`, `"html"`, etc. |
| `code`     | string | Cell content                    |

**Response:** HTML file download with `Content-Disposition: attachment; filename={title}.html`.

**Status codes:** `200 OK`

**Example:**
```bash
curl -X POST http://localhost:5000/export/html \
  -H "Content-Type: application/json" \
  -d '{"title":"Report","cells":[{"language":"python","code":"print(1)"},{"language":"markdown","code":"# Conclusion"}]}' \
  -o report.html
```

---

### 8.2 POST /export/pdf

Export a notebook as a PDF file download.

**Request body:**

| Field   | Type   | Required | Default        | Description              |
|---------|--------|----------|----------------|--------------------------|
| `title` | string | No       | `"Notebook"`   | Document title           |
| `cells` | array  | Yes      | —              | Array of cell objects    |

Each cell object: same format as HTML export.

**Response:** PDF file download with `Content-Disposition: attachment; filename={title}.pdf`.

**Status codes:** `200 OK`

**Notes:** Uses the `fpdf` library. Lines are truncated to 100 characters and encoded to Latin-1.

**Example:**
```bash
curl -X POST http://localhost:5000/export/pdf \
  -H "Content-Type: application/json" \
  -d '{"title":"Report","cells":[{"language":"python","code":"print(1)"}]}' \
  -o report.pdf
```

---

## 9. Settings

### 9.1 GET /settings

Render the settings page.

**Request:** No parameters.

**Response:** HTML page (`settings.html`) with a list of all notebooks.

**Status codes:** `200 OK`

**Example:**
```
GET /settings
```

---

## 10. Socket.IO Events

Nbook uses [Socket.IO](https://socket.io) for real-time communication. The client connects at the root path `/socket.io` with the same origin and port as the HTTP server.

### 10.1 Client → Server Events

#### 10.1.1 `connect`

Fired automatically when a WebSocket connection is established.

**Behavior:**
- In `secure` mode, validates `key` query parameter against the configured API key. Returns `False` (disconnect) on mismatch.
- Initialises the terminal: on Linux/macOS creates a PTY with bash; on Windows spawns `pwsh.exe` (or `cmd.exe` as fallback).
- Terminal output begins streaming via `terminal_output` events automatically.

**Client example:**
```js
const socket = io({ query: { key: 'my-api-key' } });
```

---

#### 10.1.2 `terminal_input`

Send input to the running terminal process.

**Payload:**
```json
{
  "input": "ls -la\n"
}
```

**Behavior:** Writes the string to the PTY or pipe stdin.

**Client example:**
```js
socket.emit('terminal_input', { input: 'python script.py\n' });
```

---

#### 10.1.3 `execute_code`

Execute code in the notebook kernel.

**Payload:**
```json
{
  "cell_id": "cell-abc123",
  "language": "python",
  "code": "print('hello')"
}
```

| Field      | Type   | Description                        |
|------------|--------|------------------------------------|
| `cell_id`  | string | Unique identifier for the cell     |
| `language` | string | Language key (e.g. `"python"`)     |
| `code`     | string | Source code to execute             |

**Server response flow:**
1. Emits `execution_started` immediately.
2. Executes the code (Python uses the stateful executor in `core/executor.py`).
3. Emits `execution_result` with the output.

**Client example:**
```js
socket.emit('execute_code', {
  cell_id: 'cell-1',
  language: 'python',
  code: 'print("hello")'
});
```

---

#### 10.1.4 `join_notebook`

Join a collaborative editing room.

**Payload:**
```json
{
  "room": "notebook-42"
}
```

| Field  | Type   | Required | Default    | Description             |
|--------|--------|----------|------------|-------------------------|
| `room` | string | No       | `"global"` | Room identifier to join |

**Behavior:** The server adds the client to the specified room. Subsequent collaborative events in that room will be broadcast to all room members.

**Client example:**
```js
socket.emit('join_notebook', { room: 'notebook-42' });
```

---

#### 10.1.5 `leave_notebook`

Leave a collaborative editing room.

**Payload:**
```json
{
  "room": "notebook-42"
}
```

| Field  | Type   | Required | Default    | Description                |
|--------|--------|----------|------------|----------------------------|
| `room` | string | No       | `"global"` | Room identifier to leave   |

**Client example:**
```js
socket.emit('leave_notebook', { room: 'notebook-42' });
```

---

#### 10.1.6 `cell_edit`

Broadcast a cell edit to other room members.

**Payload:**
```json
{
  "room": "notebook-42",
  "cell_id": "cell-abc123",
  "code": "print('updated')",
  "language": "python",
  "cursor": { "line": 3, "ch": 10 }
}
```

| Field      | Type   | Description                         |
|------------|--------|-------------------------------------|
| `room`     | string | Room to broadcast to                |
| `cell_id`  | string | Cell being edited                   |
| `code`     | string | Current cell content                |
| `language` | string | Cell language                       |
| `cursor`   | object | Cursor position for live-following  |

**Behavior:** The server re-emits the same event to all other clients in the room. The sending client does not receive its own event (`include_self=False`).

---

#### 10.1.7 `cell_add`

Broadcast a new cell to other room members.

**Payload:**
```json
{
  "room": "notebook-42",
  "cell_id": "cell-new",
  "language": "python",
  "code": ""
}
```

| Field      | Type   | Description              |
|------------|--------|--------------------------|
| `room`     | string | Room to broadcast to     |
| `cell_id`  | string | New cell identifier      |
| `language` | string | Cell language            |
| `code`     | string | Cell content             |

---

#### 10.1.8 `cell_delete`

Broadcast deletion of a cell to other room members.

**Payload:**
```json
{
  "room": "notebook-42",
  "cell_id": "cell-abc123"
}
```

| Field     | Type   | Description              |
|-----------|--------|--------------------------|
| `room`    | string | Room to broadcast to     |
| `cell_id` | string | Cell to remove           |

---

#### 10.1.9 `cell_reorder`

Broadcast cell reordering to other room members.

**Payload:**
```json
{
  "room": "notebook-42",
  "order": ["cell-1", "cell-2", "cell-3"]
}
```

| Field   | Type   | Description                         |
|---------|--------|-------------------------------------|
| `room`  | string | Room to broadcast to                |
| `order` | array  | Ordered array of cell IDs           |

---

#### 10.1.10 `nb_title`

Broadcast a notebook title change to other room members.

**Payload:**
```json
{
  "room": "notebook-42",
  "title": "My Renamed Notebook"
}
```

| Field   | Type   | Description              |
|---------|--------|--------------------------|
| `room`  | string | Room to broadcast to     |
| `title` | string | New notebook title       |

---

### 10.2 Server → Client Events

#### 10.2.1 `terminal_output`

Streamed terminal output from the PTY or subprocess pipe.

**Payload:**
```json
{
  "output": "user@host:~$ ls\n"
}
```

| Field    | Type   | Description           |
|----------|--------|-----------------------|
| `output` | string | Terminal output chunk |

**Frequency:** Emitted continuously as data is read from the terminal (every ~10ms).

---

#### 10.2.2 `execution_started`

Emitted when a code execution request begins processing.

**Payload:**
```json
{
  "cell_id": "cell-abc123"
}
```

| Field     | Type   | Description              |
|-----------|--------|--------------------------|
| `cell_id` | string | Cell being executed      |

---

#### 10.2.3 `execution_result`

Emitted when code execution completes.

**Payload:**
```json
{
  "cell_id": "cell-abc123",
  "output": "hello\n",
  "status": "success"
}
```

| Field     | Type   | Description                  |
|-----------|--------|------------------------------|
| `cell_id` | string | Cell that was executed       |
| `output`  | string | Captured stdout/result       |
| `status`  | string | `"success"` or `"error"`     |

---

#### 10.2.4 `cell_edit`

Broadcasted to all other clients in a room when a user edits a cell.

**Payload:** Same as the incoming `cell_edit` (see §10.1.6).

---

#### 10.2.5 `cell_add`

Broadcasted to all other clients in a room when a user adds a cell.

**Payload:** Same as the incoming `cell_add` (see §10.1.7).

---

#### 10.2.6 `cell_delete`

Broadcasted to all other clients when a cell is deleted.

**Payload:** Same as the incoming `cell_delete` (see §10.1.8).

---

#### 10.2.7 `cell_reorder`

Broadcasted to all other clients when cells are reordered.

**Payload:** Same as the incoming `cell_reorder` (see §10.1.9).

---

#### 10.2.8 `nb_title`

Broadcasted to all other clients when the notebook title changes.

**Payload:** Same as the incoming `nb_title` (see §10.1.10).

---

## Security

### API Key Authentication

When the server runs with `NBOOK_MODE=secure`, all HTTP requests (except `/static` and `/socket.io`) must include the API key:

- **Query parameter:** `?key=YOUR_API_KEY`
- **HTTP header:** `X-API-KEY: YOUR_API_KEY`

If the key is missing or invalid:
- JSON/API requests receive an HTTP `403 Forbidden` response.
- Page requests receive an HTML error page with `403` status.

Socket.IO connections must pass `key` as a query parameter during the handshake:
```js
const socket = io({ query: { key: 'YOUR_API_KEY' } });
```

### Path Traversal Protection

All file endpoints validate paths via `get_safe_path()`, which resolves the requested path against the configured `WORKSPACE` directory and rejects paths that escape it. This prevents directory traversal attacks.

### File Upload Restrictions

Uploaded files are blocked if they have one of the following extensions: `.exe`, `.bat`, `.cmd`, `.com`, `.msi`, `.scr`, `.pif`, `.sh`, `.pyc`, `.dll`, `.so`, `.dylib`, `.vbs`, `.ps1`, `.app`.

The filename is sanitised with `os.path.basename()` to strip any directory components.

---

## Appendix: Summary Table

### HTTP Endpoints

| Method | Path                     | Description               |
|--------|--------------------------|---------------------------|
| GET    | /auth/register           | Register form             |
| POST   | /auth/register           | Create account            |
| GET    | /auth/login              | Login form                |
| POST   | /auth/login              | Authenticate              |
| POST   | /auth/logout             | Clear session             |
| GET    | /auth/me                 | Check auth status         |
| GET    | /auth/profile            | Profile page              |
| POST   | /auth/profile            | Update profile            |
| GET    | /                        | Main editor               |
| GET    | /system/stats            | System stats              |
| POST   | /system/restart          | Restart kernel + globals  |
| GET    | /files/list              | List files                |
| GET    | /files/read              | Read file                 |
| POST   | /files/delete            | Delete file/dir           |
| POST   | /files/rename            | Rename file/dir           |
| POST   | /save-file               | Save file content         |
| POST   | /files/upload            | Upload file               |
| GET    | /files/download          | Download file             |
| POST   | /files/create            | Create file/dir           |
| GET    | /variables               | List Python variables     |
| POST   | /kernel/restart          | Clear Python globals      |
| POST   | /kernel/cancel           | Cancel execution          |
| POST   | /git/clone               | Clone git repo            |
| POST   | /save                    | Save/update project       |
| GET    | /history                 | Project history page      |
| GET    | /history/load/{id}       | Load project              |
| POST   | /history/delete/{id}     | Delete project            |
| POST   | /history/rename/{id}     | Rename project            |
| GET    | /history/export/{id}     | Export as .npy            |
| POST   | /export/html             | Export as HTML            |
| POST   | /export/pdf              | Export as PDF             |
| GET    | /settings                | Settings page             |

### Socket.IO Events

| Direction | Event              | Description                 |
|-----------|--------------------|-----------------------------|
| C→S       | connect            | Connect + init terminal     |
| C→S       | terminal_input     | Send terminal input         |
| C→S       | execute_code       | Execute code in kernel      |
| C→S       | join_notebook      | Join collaboration room     |
| C→S       | leave_notebook     | Leave collaboration room    |
| C→S       | cell_edit          | Broadcast cell edit         |
| C→S       | cell_add           | Broadcast cell add          |
| C→S       | cell_delete        | Broadcast cell delete       |
| C→S       | cell_reorder       | Broadcast cell reorder      |
| C→S       | nb_title           | Broadcast title change      |
| S→C       | terminal_output    | Stream terminal output      |
| S→C       | execution_started  | Execution started           |
| S→C       | execution_result   | Execution completed         |
| S→C       | cell_edit          | Collaborative cell edit     |
| S→C       | cell_add           | Collaborative cell add      |
| S→C       | cell_delete        | Collaborative cell delete   |
| S→C       | cell_reorder       | Collaborative reorder       |
| S→C       | nb_title           | Collaborative title change  |
