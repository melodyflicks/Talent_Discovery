# AI-Powered Talent Discovery & Employee Profiling - Backend

A modular Python + FastAPI backend service with PostgreSQL, SQLAlchemy, Pydantic, and JWT authentication.

## Stack & Architecture

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **ORM & Database**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + [PostgreSQL](https://www.postgresql.org/) (driver: `psycopg` v3)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/latest/)
- **Authentication**: JWT Bearer tokens (`python-jose`) + secure password hashing (`passlib` with `bcrypt`)
- **Database Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Testing**: [Pytest](https://docs.pytest.org/) + `httpx` + SQLite in-memory test harness

## Project Layout

```
backend/
├── alembic/                  # Alembic database migration scripts
│   ├── versions/             # Migration revision files
│   └── env.py
├── app/
│   ├── api/                  # API routers (auth, employees, profiles, skills, roles, matching, etc.)
│   ├── core/                 # Core configuration and security/auth dependencies
│   ├── db/                   # Database session, base models, and seed script
│   ├── models/               # SQLAlchemy 2.0 domain models
│   ├── schemas/              # Pydantic request & response schemas
│   ├── services/             # Modular service layer (ready for future AI pipeline)
│   ├── integrations/         # Future external integrations (GitHub, LinkedIn, LMS)
│   └── main.py               # FastAPI application entrypoint
├── requirements.txt
├── alembic.ini
└── README.md
```

## Quick Start (Local Setup)

### 1. Create and activate a virtual environment

```bash
cd "D:\buildathon 2\backend"

# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Ensure `DATABASE_URL` matches your local PostgreSQL configuration:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/talent_discovery
JWT_SECRET=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEFAULT_ADMIN_PASSWORD=AdminPassword123!
DEFAULT_HR_PASSWORD=HRPassword123!
CORS_ORIGINS=http://localhost:5173
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Seed initial data

```bash
python ../data/seeds/seed_database.py
```

### 6. Start FastAPI server

```bash
uvicorn app.main:app --reload --port 8000
```

- API Server: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc API Docs: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/api/health`

## Demo HR / Admin Accounts

> [!NOTE]
> Demo accounts are provided for local evaluation and testing purposes only. Passwords can be configured via environment variables (`DEFAULT_ADMIN_PASSWORD` / `DEFAULT_HR_PASSWORD`).

| Role | Email | Default Password |
|---|---|---|
| **Admin** | `admin1@talent.local` | `AdminPassword123!` |
| **Admin** | `admin2@talent.local` | `AdminPassword123!` |
| **HR Lead** | `hr1@talent.local` | `HRPassword123!` |
| **HR Specialist** | `hr2@talent.local` | `HRPassword123!` |
| **Employee** | `alex.chen@talent.local` | `EmployeePassword123!` |

## Running Tests

Run the backend test suite (uses fast in-memory SQLite):

```bash
pytest -v tests/backend
```
