# Setup & Installation Guide

This guide outlines the working setup sequence for the **AI-Powered Talent Discovery & Employee Profiling** backend.

---

## 1. Prerequisites & PostgreSQL Running

- **Python**: Version 3.10+ (tested on Python 3.13)
- **PostgreSQL**: Version 14+ / 18.x running on `localhost:5432`

---

## 2. Create the Database

Create the dedicated PostgreSQL database:

```sql
psql -U postgres
CREATE DATABASE talent_discovery;
```

---

## 3. Configure `backend/.env`

Create `backend/.env` (ignored by Git) and configure your local credentials:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/talent_discovery

JWT_SECRET=CHANGE_THIS_TO_A_RANDOM_SECRET
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

DEFAULT_ADMIN_PASSWORD=CHANGE_ADMIN_PASSWORD
DEFAULT_HR_PASSWORD=CHANGE_HR_PASSWORD

LLM_PROVIDER=gemini
GEMINI_API_KEY=
OPENAI_API_KEY=
```

> [!IMPORTANT]
> Never commit `.env` or expose database credentials in source code.

---

## 4. Run Alembic Migrations

From the backend directory with virtual environment activated:

```bash
cd "D:\buildathon 2\backend"
.\.venv\Scripts\activate
alembic upgrade head
```

This creates all 13 core domain tables:
- `users`
- `employee_profiles`
- `external_profiles`
- `skills`
- `employee_skills`
- `skill_evidence`
- `roles`
- `role_skills`
- `role_matches`
- `skill_gaps`
- `courses`
- `course_recommendations`
- `learning_roadmaps`
- `alembic_version`

---

## 5. Run Database Seed Script

Populate the initial catalog, HR/Admin accounts, and realistic demo data:

```bash
python ..\data\seeds\seed_database.py
```

Seeded records include:
- 2 Admin accounts (`admin1@talent.local`, `admin2@talent.local`)
- 2 HR accounts (`hr1@talent.local`, `hr2@talent.local`)
- 12 Demo employee accounts and profiles across 7 departments
- 24 Standardized skills taxonomy
- 7 Core organizational roles and required proficiencies
- 8 Learning courses with provider mappings
- Pre-evaluated role matches, skill gaps, course recommendations, and career roadmaps

The seed process is fully idempotent and safe to run multiple times.

---

## 6. Start FastAPI Application

Launch the live Uvicorn development server:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## 7. Open API Documentation

Access the interactive API explorer and Swagger UI:
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 8. Test Authentication & API

### Health Verification
```bash
curl http://localhost:8000/api/health
```
Response:
```json
{
  "status": "ok",
  "database": "connected"
}
```

### Admin Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"admin1@talent.local\", \"password\": \"<DEFAULT_ADMIN_PASSWORD>\"}"
```

### HR Analytics (Protected)
```bash
curl http://localhost:8000/api/hr/analytics \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Run Automated Tests
```bash
pytest -v tests/backend
```
