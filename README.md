# Municipal Integrity & Bribe-Free Service Portal (MIBSP)

Production-oriented Flask + MySQL complaint management portal for municipal anti-corruption workflows.

## Highlights
- Anonymous citizen complaint submission with evidence upload and tracking ID (`MIBXXXXXXXX`).
- Role-based officer/admin workflows with strict status transitions.
- Append-only, hash-chained audit logs for accountability.
- Public transparency dashboard with Chart.js analytics.
- Secure defaults: CSRF, PBKDF2-SHA256, secure uploads, session timeout.

## Stack
- **Presentation:** HTML5, CSS3, Bootstrap 5, Vanilla JS, Chart.js
- **Application:** Flask Blueprints, MVC-ish separation, session auth, role decorators
- **Data:** MySQL-ready schema via SQLAlchemy models (3NF-oriented with FKs + indexes)

## Project Structure
```
app/
├── models/
├── routes/
├── static/
├── templates/
└── utils/
```

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app.py db init
flask --app app.py db migrate -m "initial"
flask --app app.py db upgrade
flask --app app.py seed
python app.py
```

## Security Controls
- PBKDF2-SHA256 password hashing.
- CSRF protection on forms.
- Parameterized ORM queries.
- 16MB upload cap + extension whitelist + `secure_filename`.
- Role-based route guards and direct URL protection.
- 8-hour session timeout.
- Citizen anonymity preserved (no citizen login/IP storage for complaints).

## Testing
```bash
pytest -q
```

## Deployment
- Uses env-based config from `config.py`.
- Supports `DevelopmentConfig` and `ProductionConfig`.
- WSGI-compatible entrypoint: `app.py`.
- Suitable for Render, Railway, PythonAnywhere, and AWS EC2.
