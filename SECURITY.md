# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Nbook, please report it privately by emailing the project maintainers. **Do not open a public issue.**

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## What to Include

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigation (optional)

## Scope

The following are considered in scope:
- Remote code execution
- Cross-site scripting (XSS)
- Cross-site request forgery (CSRF)
- Path traversal
- Authentication bypass
- Data exposure

## Safe Harbor

We will not take legal action against researchers who:
- Report vulnerabilities in good faith
- Do not access or modify user data beyond what is necessary to demonstrate the issue
- Do not exploit the vulnerability beyond the minimum required to prove its existence
- Follow this disclosure policy

## Security Best Practices for Users

- **Run in secure mode** in production: `python app.py start`
- **Set a strong SECRET_KEY** in your `.env` file
- **Use HTTPS** behind a reverse proxy (Nginx, Caddy)
- **Keep dependencies updated** with `pip install --upgrade -r requirements.txt`
- **Use Redis** for rate limiting in multi-process deployments
