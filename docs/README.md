# Nbook

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Language](https://img.shields.io/badge/Language-Python-blue.svg)
![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)

Nbook is a web-based interactive notebook environment, offering a "glass interface" for code execution, terminal access, and project management. It aims to provide a seamless and intuitive experience for developers and data scientists, combining the power of a traditional IDE with the flexibility of an interactive notebook.

## Features

*   **Interactive Code Execution:** Run Python code cells with stateful execution, magic commands (`!`), and integrated Matplotlib plotting support.
*   **Integrated Terminal:** Full-featured terminal access directly within the web interface using Xterm.js, allowing for command-line operations without leaving the browser.
*   **File Explorer:** Manage your project workspace with an intuitive file browsing, creation, editing, and deletion experience.
*   **Git Integration:** Clone repositories directly into your workspace, facilitating version control and collaborative development.
*   **Real-time System Monitoring:** Monitor RAM and disk usage directly from the interface, providing insights into resource consumption.
*   **Project History & Management:** Save, load, rename, export, and delete notebooks, maintaining a clear project history and enabling easy project switching.
*   **Secure & Free Modes:** Operate Nbook in a secure mode with API key protection for controlled access, or a free mode for local development and unrestricted use.
*   **Notebook Conversion:** Convert Nbook project files (`.npy` or `.ngo`) into organized code folders, making it easy to extract and reuse code.
*   **Modern Web Interface:** Built with Flask, Flask-SocketIO, CodeMirror, Tailwind CSS, and jQuery for a responsive, dynamic, and aesthetically pleasing user experience.
*   **Persistent Storage:** Notebooks are stored in an SQLite database using Flask-SQLAlchemy, ensuring your work is saved across sessions.

## Architecture Overview

Nbook is built as a Flask web application with a strong emphasis on real-time interaction using WebSockets.

*   **Backend (Flask):** Handles HTTP requests for file operations, project management, system stats, and serves the web pages.
*   **Real-time Communication (Flask-SocketIO):** Powers the interactive code execution and integrated terminal, enabling bi-directional communication between the client and server.
*   **Core Logic (`core` module):** Contains the application's business logic, including:
    *   `executor.py`: Manages Python code execution, state, and plotting.
    *   `routes.py`: Defines API endpoints and SocketIO event handlers.
    *   `terminal.py`: Handles server startup modes and notebook conversion.
    *   `cli.py`: Provides command-line interface for Nbook.
    *   `__init__.py`: Initializes Flask extensions (DB, SocketIO) and defines the `Notebook` database model.
*   **Frontend (HTML/CSS/JS):**
    *   **Templates (`templates`):** Rendered using Jinja2, providing the structure of the web interface.
    *   **Styling (Tailwind CSS):** For a modern, utility-first design.
    *   **Interactive Components:**
        *   **CodeMirror:** For syntax highlighting and code editing in cells.
        *   **Xterm.js:** For the fully functional integrated terminal.
        *   **jQuery:** For DOM manipulation and AJAX calls.
        *   **Socket.IO Client:** For real-time communication with the backend.
*   **Data Persistence (SQLite/Flask-SQLAlchemy):** Stores notebook content and metadata.
*   **Workspace Management:** Uses a dedicated `workspace` directory for file explorer operations.

## Installation

To set up Nbook locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rkriad585/Nbook.git
    cd Nbook
    ```

2.  **Install dependencies:**
    Nbook requires Python and several libraries. It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    # Create a virtual environment
    python -m venv venv
    # Activate the virtual environment
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate

    # Install required Python packages
    pip install Flask Flask-SQLAlchemy Flask-SocketIO GitPython psutil Click matplotlib
    ```

## Usage Example

After installation, you can start the Nbook server in either free or secure mode using the command-line interface.

1.  **Start in Free Mode:**
    This mode is ideal for local development, testing, and personal use. It does not require an API key for access.
    ```bash
    python app.py free
    ```
    Access your Nbook instance at `http://127.0.0.1:5000`.

2.  **Start in Secure Mode:**
    This mode generates a unique API key for access, enhancing security for deployments where access control is desired.
    ```bash
    python app.py start
    ```
    The console will display a URL with the generated API key (e.g., `http://127.0.0.1:5000?key=YOUR_API_KEY`). You must use this key in the URL or as an `X-API-KEY` header for all requests.

3.  **Convert a Notebook:**
    If you have an Nbook project file (e.g., `my_project.npy` or `.ngo`), you can convert it to a standard code folder containing Python, HTML, and Markdown files.
    ```bash
    python app.py convert my_project.npy
    ```
    This will create a new directory (e.g., `my_project_project`) with the extracted code.

## Configuration

Nbook's configuration is managed via `config.py`. Key settings include:

*   `SECRET_KEY`: Used by Flask for session management.
*   `SQLALCHEMY_DATABASE_URI`: Path to the SQLite database (`data/nbook.db`).
*   `WORKSPACE`: Directory for file explorer operations (`workspace/`).
*   `NBOOK_MODE`: `free` or `secure`, set at runtime by CLI commands.
*   `NBOOK_API_KEY`: Generated in secure mode.

For more details, refer to `docs/CONFIGURATION.md`.

## Development

### Project Structure

```
.
├── app.py                  # Main Flask application entry point
├── config.py               # Application configuration
├── core                    # Core application logic
│   ├── __init__.py         # Flask extensions, DB model
│   ├── cli.py              # Command Line Interface (CLI) commands
│   ├── executor.py         # Python code execution and state management
│   ├── routes.py           # Flask routes and SocketIO event handlers
│   └── terminal.py         # Server startup modes and notebook conversion
├── docs                    # Project documentation (this folder)
├── static                  # Static assets (CSS, JS, images)
│   └── images
│       └── logo.svg
└── templates               # Jinja2 HTML templates
    ├── base.html           # Base template for all pages
    ├── error.html          # Error page for access denied
    ├── history.html        # Project history page
    └── index.html          # Main interactive notebook editor
```

### Running Tests

*(No explicit tests provided in the codebase context, but this is a common section)*
To ensure stability and functionality, it is recommended to implement unit and integration tests.

### Frontend Development

The frontend uses Tailwind CSS for styling and relies heavily on CodeMirror for code editing, Xterm.js for terminal emulation, and Socket.IO for real-time updates. JavaScript logic in `index.html` orchestrates these components.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and ensure they adhere to the project's coding style.
4.  Write clear, concise commit messages.
5.  Push your branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

written by Neorwc