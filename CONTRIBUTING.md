# Contributing to Nbook

Thanks for your interest in contributing! Here's how you can help.

## Getting Started

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/nbook.git
   ```
3. Set up a development environment:
   ```bash
   cd nbook
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   .\venv\Scripts\Activate    # Windows
   pip install -r requirements.txt
   ```
4. Create a branch for your work:
   ```bash
   git checkout -b my-feature
   ```

## Development Workflow

- **Start the app:** `python app.py free`
- **Run tests:** `python -m pytest tests/ -v`
- **Check code style:** ensure consistency with the existing codebase

## Pull Request Guidelines

- Keep changes focused and minimal.
- Write clear commit messages following conventional commits (e.g., `feat: add dark mode`).
- Ensure all tests pass before submitting.
- Update documentation if you add or change features.
- Reference any related issues in your PR description.

## Code Style

- **Python:** Follow PEP 8. Use expressive variable names.
- **JavaScript:** Use `const`/`let`, avoid `var`. Use double quotes for strings.
- **Templates:** Use double-quoted HTML attributes, keep consistent indentation.
- **CSS:** Use Tailwind utility classes where possible.

## Reporting Issues

Open an issue with:
- A clear, descriptive title
- Steps to reproduce (if a bug)
- Expected vs actual behavior
- Screenshots or logs if helpful

## Feature Requests

Suggest ideas by opening an issue with the label `enhancement`. Describe the feature, why it's useful, and any implementation ideas you have.

## Code of Conduct

This project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.
