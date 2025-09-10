# Secure Donation Site (HTML/CSS + Flask API + MySQL)

A deployment-ready starter that uses HTML/CSS for the frontend, Flask for the API/backend, and MySQL for the database. It includes protections against SQL Injection (via SQLAlchemy ORM), CSRF (Flask-WTF), security headers (Flask-Talisman), password hashing (bcrypt), and basic rate limiting (Flask-Limiter).

## Features
- Static HTML/CSS UI rendered via Flask templates (no JS required)
- User registration/login with bcrypt-hashed passwords
- Create "needs" (requests) and "donations"
- REST-like JSON API endpoints under `/api/*`
- CSRF protection for all forms
- Security headers (CSP, HSTS, X-Frame-Options, etc.)
- Parameterized DB access with SQLAlchemy ORM
- Rate limiting on sensitive endpoints

## Quick Start (Local)
1. **Install system deps**: Ensure Python 3.10+ and MySQL are installed.
2. **Create DB** in MySQL:
   ```sql
   CREATE DATABASE secure_donation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'secure_user'@'localhost' IDENTIFIED BY 'change-this-strong';
   GRANT ALL PRIVILEGES ON secure_donation_db.* TO 'secure_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. **Clone/Extract** this folder and create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   # then edit DATABASE_URL to:
   # mysql://secure_user:change-this-strong@localhost:3306/secure_donation_db
   # and set a strong SECRET_KEY
   ```
4. **Create virtualenv & install**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Initialize DB tables**:
   ```bash
   python app.py --init-db
   ```
6. **Run**:
   ```bash
   flask --app app:app run --host=0.0.0.0 --port=5000
   ```

## Production Notes
- Use `gunicorn` behind Nginx:
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 app:app
  ```
- Serve static files via Nginx directly when possible.
- Keep `.env` secrets out of version control.
- Set `SESSION_COOKIE_SECURE=True` when using HTTPS.
- Use a WAF or reverse proxy with rate limiting, and enable HTTPS/HSTS.

## API Overview
- `POST /api/register`, `POST /api/login`
- `GET /api/needs`, `POST /api/needs`
- `GET /api/donations`, `POST /api/donations`
- All unsafe methods require CSRF tokens (send as `X-CSRFToken` header or form hidden field).

## Security
- **CSRF**: All form posts are protected by Flask-WTF's CSRF.
- **SQL Injection**: All DB access via SQLAlchemy ORM / parameterized queries.
- **Auth**: Passwords hashed with bcrypt.
- **Headers**: Enforced by Flask-Talisman (CSP, HSTS, frame-ancestors, etc.).
- **Rate Limiting**: Flask-Limiter applied to login/register and API POSTs.
