# Nbook Development Plan

## Priority 1: Security Hardening

- [x] Rate limiting on API endpoints (Flask-Limiter)
- [x] Socket.IO authentication (validate API key on connect)
- [x] Content Security Policy (CSP) headers
- [x] Secure cookie configuration (SameSite, HttpOnly)
- [x] File upload size limits and type validation
- [x] Execution timeout guard for shell commands
- [x] Input sanitization on all file operations

## Priority 2: Developer Experience

- [x] Cell reordering (drag-and-drop)
- [x] In-browser file editor (edit files directly in UI)
- [x] Auto-save notebook every 30 seconds
- [x] Search across notebook cells
- [x] Better error pages (404, 500)

## Priority 3: Infrastructure

- [x] Dockerfile + docker-compose.yml
- [x] GitHub Actions CI/CD
- [x] Unit tests for core modules (27 tests)

## Priority 4: Advanced Features

- [ ] User authentication (login/register)
- [ ] Collaborative editing via WebSockets
- [ ] Plugin/extension system
- [ ] Export to PDF via weasyprint
- [ ] Dark/light syntax theme selector per cell
