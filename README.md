# Nbook

![Logo](https://github.com/rkriad585/Nbook/blob/main/static/images/logo.svg)


![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Language](https://img.shields.io/badge/Language-Python-blue.svg)
![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)

Nbook is a web-based interactive notebook environment, offering a "glass interface" for code execution, terminal access, and project management.

## Features

*   **Interactive Code Execution:** Run Python code cells with stateful execution, magic commands (`!`), and integrated Matplotlib plotting support.
*   **Integrated Terminal:** Full-featured terminal access directly within the web interface using Xterm.js.
*   **File Explorer:** Manage your project workspace with an intuitive file browsing and editing experience.
*   **Git Integration:** Clone repositories directly into your workspace.
*   **Real-time System Monitoring:** Monitor RAM and disk usage directly from the interface.
*   **Project History & Management:** Save, load, rename, export, and delete notebooks, maintaining a clear project history.
*   **Secure & Free Modes:** Operate Nbook in a secure mode with API key protection or a free mode for local development.
*   **Notebook Conversion:** Convert Nbook project files (`.npy` or `.ngo`) into organized code folders.
*   **Modern Web Interface:** Built with Flask, Flask-SocketIO, CodeMirror, Tailwind CSS, and jQuery for a responsive and dynamic user experience.
*   **Persistent Storage:** Notebooks are stored in an SQLite database using Flask-SQLAlchemy.

## Installation

To set up Nbook locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rkriad585/Nbook.git
    cd Nbook
    ```

2.  **Install dependencies:**
    Nbook requires Python and several libraries. It's recommended to use a virtual environment.
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-SocketIO GitPython psutil Click matplotlib
    ```

## Usage Example

After installation, you can start the Nbook server in either free or secure mode:

1.  **Start in Free Mode:**
    This mode is ideal for local development and does not require an API key.
    ```bash
    python app.py free
    ```
    Access your Nbook instance at `http://127.0.0.1:5000`.

2.  **Start in Secure Mode:**
    This mode generates a unique API key for access, enhancing security.
    ```bash
    python app.py start
    ```
    The console will display a URL with the generated API key (e.g., `http://127.0.0.1:5000?key=YOUR_API_KEY`).

3.  **Convert a Notebook:**
    If you have an Nbook project file (e.g., `my_project.npy`), you can convert it to a standard code folder:
    ```bash
    python app.py convert my_project.npy
    ```

## License

This project is licensed under the MIT License.

written by Neorwc
