# AI-Powered Talent Discovery & Employee Profiling Platform

A local-first foundation for discovering employee capabilities, profiling skills, matching internal opportunities, and planning learning journeys. This initial phase supplies the project layout and runnable frontend/backend shells; the intelligence workflows are intentionally scheduled for later phases.

## Problem

Organizations often know job titles but not the full set of skills employees have gained through projects, learning, and adjacent roles. The platform will assemble evidence-backed profiles to support internal mobility and workforce planning.

## Architecture

React/Vite provides the UI; FastAPI exposes a versioned API; SQLAlchemy is prepared for PostgreSQL and pgvector. The `ai/` package isolates resume, LLM, embedding, matching, and recommendation boundaries. JSON files provide safe local demo catalog data when optional external integrations are not configured.

## Stack

React, Vite, Bootstrap 5, React-Bootstrap, Recharts, Python, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, and pgvector.

## Local setup

1. Copy `.env.example` to `.env` and supply only the services you intend to use.
2. Frontend: `cd frontend`, `npm install`, then `npm run dev` (http://localhost:5173).
3. Backend: `cd backend`, create/activate a virtual environment, run `pip install -r requirements.txt`, then `uvicorn app.main:app --reload` (http://localhost:8000; docs at `/docs`).
4. Set `DATABASE_URL` to a PostgreSQL database with pgvector enabled before building persistence features. The startup shell does not create schema or seed production data.

## Layout

- `frontend/` — Vite UI and route pages.
- `backend/` — FastAPI application, persistence boundary, and external adapters.
- `ai/` — isolated pipeline and provider interfaces.
- `data/` — local skill, role, course, and demo catalogs.
- `docs/` — architecture and phase documentation.
- `tests/` — initial smoke tests.

## Environment and AI configuration

Set `LLM_PROVIDER` to `gemini` or `openai`, then provide the matching key. Providers are selected through `ai/llm/llm_service.py`; no network call is made by the scaffold. Never commit `.env`.

## Development phases

1. Foundation (current): application shells, contracts, configuration, and local catalogs.
2. Profile ingestion: resume processing and evidence storage.
3. Intelligence: normalization, inference, matching, gaps, and recommendations.
4. Product workflows: career assistant, HR analytics, feedback, and evaluation.

See [docs/setup.md](docs/setup.md) for setup details and the remaining documents for design boundaries.
