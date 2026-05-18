# Nbook Development Plan

## Priority 1: Security Hardening

- [ ] Rate limiting on API endpoints (Flask-Limiter)
- [ ] Socket.IO authentication (validate API key on connect)
- [ ] Content Security Policy (CSP) headers
- [ ] Secure cookie configuration (SameSite, HttpOnly)
- [ ] File upload size limits and type validation
- [ ] Execution timeout guard for Python cells
- [ ] Input sanitization on all file operations

## Priority 2: Developer Experience

- [ ] Cell reordering (drag-and-drop)
- [ ] In-browser file editor (edit files directly in UI)
- [ ] Auto-save notebook every 30 seconds
- [ ] Search across notebook cells
- [ ] Better error pages (404, 500)
- [ ] Loading spinners for slow operations

## Priority 3: Infrastructure

- [ ] Dockerfile + docker-compose.yml
- [ ] GitHub Actions CI/CD
- [ ] Unit tests for core modules
- [ ] Request logging middleware

## Priority 4: Advanced Features

- [ ] User authentication (login/register)
- [ ] Collaborative editing via WebSockets
- [ ] Plugin/extension system
- [ ] Export to PDF via weasyprint
- [ ] Dark/light syntax theme selector per cell
