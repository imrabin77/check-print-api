# Check Print API

FastAPI backend for the Check Print System.

## Tech Stack
- **Runtime**: Python 3.12
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 16
- **Auth**: JWT (python-jose + passlib/bcrypt)
- **PDF**: ReportLab

## Quick Start

```bash
# With Docker
docker compose up --build

# Without Docker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://cps_user:cps_secret_password@localhost:5432/checkprint` | Async PG connection string |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | JWT signing key |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed CORS origins (JSON array) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Token TTL |

## Seeded Users

| Email | Password | Role |
|---|---|---|
| `admin@checkprint.local` | `admin123` | ADMIN |
| `clerk@checkprint.local` | `clerk123` | CLERK |
| `viewer@checkprint.local` | `viewer123` | VIEWER |

## API Docs

Once running: `http://localhost:8000/docs`
